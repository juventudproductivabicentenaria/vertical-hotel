odoo.define('hotel_reservation.ReservationWebsite', function (require) {

	"use strict";

	//alert("Diomedes")

	var publicWidget = require('web.public.widget');
	var core = require('web.core');
	var qweb = core.qweb;

	console.log("Perfecto");

	publicWidget.registry.reservationWebsite = publicWidget.Widget.extend({

		selector: '#reservation', //id
		xmlDependencies: ['/hotel_reservation/static/src/xml/search_reservation.xml',
			'/hotel_reservation/static/src/xml/rooms_available.xml',
		],

		events: {
			'click #busqueda': '_onNextBlogClick',
			'click #button_reserva': '_onNextReservar',
			'click #incremento_adults': '_sumar_adults',
			'click #incremento_ninos': '_sumar_ninos',
			'click #desminuir_adults': '_resta_adults',
			'click #desminuir_ninos': '_resta_ninos',
			'click .checkbox': '_mostrarBoton',
			'click .dropdown-menu': '_stop_boton',
    	},

		start: function () {
			console.log('Se ejecuta')
            var self = this;
            var def = this._super.apply(this, arguments);
			this._fetch().then(this._render.bind(this));
            },
			
           /**
         * @private
         */
        _fetch: function () {
			console.log('_fetch')
            return this._rpc({
                route: "/reservation/date_updated",
            }).then(res => {
				console.log(typeof res)
				return res;
			})
        },

		/**
         * @private
         */
		_render: function (res) {
			console.log('render');
			var date_from = res.date_from
			var date_until = res.date_to
			this.webProperty =  $(qweb._render('hotel_reservation.search_reservation', {
				date_from: date_from,
				date_until: date_until,
			}));
			console.log(this.webProperty);
			this._addEstructureCategories();
        },

		_addEstructureCategories: function () {
			console.log('_addEstructureCategories')
            var categoriesHtml = this.webProperty;
			var roomHtml = this.rooms_available;
            this.$('.search_reserva').html(categoriesHtml)
			if (roomHtml) {
				console.log('Si se cumple');
				this.$('.rooms_available').html(roomHtml)
			};
        },

		_stop_boton: function(event) {

			//Funcion para que el boton no puede cerrarse

			event.stopPropagation();
			console.log('Stop');
			console.log('Stop');
		},

		_sumar_adults: function (ev){

			var number = Number(document.getElementById("evaluar_adults").value);

			if (number >=0 && number < 5) {

				console.log('adults_suma')

				number += 1;

				document.getElementById("resultado_adults").innerHTML = eval(number);
				document.getElementById("evaluar_adults").value = number;
			};
		},

		_resta_adults: function(ev){

			var number = Number(document.getElementById("evaluar_adults").value);

			if (number > 0) {

				console.log('Resta')

				number -= 1;

				document.getElementById("resultado_adults").innerHTML = eval(number);
				document.getElementById("evaluar_adults").value = number;
			}

		},

		_sumar_ninos: function (ev){

			var number = Number(document.getElementById("evaluar_ninos").value);

			if (number >=0 && number < 5) {

				console.log('ninos_suma')

				number += 1;

				document.getElementById("resultado_ninos").innerHTML = eval(number);
				document.getElementById("evaluar_ninos").value = number;
			};
		},

		_resta_ninos: function(ev){

			var number = Number(document.getElementById("evaluar_ninos").value);

			if (number > 0) {

				console.log('Resta')

				number -= 1; 

				document.getElementById("resultado_ninos").innerHTML = eval(number);
				document.getElementById("evaluar_ninos").value = number;
			}

		},

		_mostrarBoton: function (ev){
			var button_reserva = document.getElementById('button_reserva');
			var al_menos_uno = false;
			var checkedo = $(".checkbox:checked").length

			if (checkedo >= 1) {
				console.log('Es mayor')
				button_reserva.style.display = 'inline';
			} else {
				console.log('No es mayor')
				button_reserva.style.display = 'none';
			}
		},

	    _onNextBlogClick: function (ev) {
			console.log('Paso 2')

			var date_from = $('#dateFrom').val(); //Para obtener valor de html
			var date_until = $('#date_until').val()
			var adults = $('#evaluar_adults').val()
			var ninos = $('#evaluar_ninos').val()
			var self = this;

			if (date_from > date_until) {
				return alert("La fecha de salida debe ser mayor que la fecha de llegada.")
			}
			this._rpc({
				route: '/reservation/search_reservation',
				params: {
					'date_from': date_from,
					'date_until': date_until,
					'adults': adults,
					'ninos': ninos,
				},
			}).then(data => {
				self._render_onNextBlogClick(data);
			});
	    },
		_render_onNextBlogClick: function (data) {
			var room = data.rooms_list;
			console.log(room)
			this.rooms_available =  $(qweb._render('hotel_reservation.rooms_available', {
				room: room,
			}));
			this._addEstructureCategories();
		},


	    _onNextReservar: function (ev) {
			console.log('ButtonReserva')

			var checkbox = $('[name="reserva"]:checked').map(function(){
				return this.value;
			  }).get();
			var date_from = $('#dateFrom').val();
			var date_until = $('#date_until').val();
			var adults = $('#evaluar_adults').val();
			var ninos = $('#evaluar_ninos').val();
			var self = this;
			// var fecha =  new Date();
			// var fecha_datefrom =  new Date(date_from);
			// var dia_datefrom = fecha_datefrom.getDate() + 1;
			// var today = fecha.getDate();

			this._rpc({
				route: '/reservation/reserved_rooms',
				params: {
					'ids': checkbox,
					'date_from': date_from,
					'date_until': date_until,
					'adults': adults,
					'ninos': ninos,
				},
			}).then(data => {
				console.log(data)
				// if (dia_datefrom === today || Number(adults) === 0) {
				if (data.error_validation) {
					self.showerror(data.error_validation);
				}else{
					window.location = '/reserved/' + `${data.reservation_id}`+ '?reserve=True'

				}
			});
	    },

		showerror: function (responseText) {
			console.log('showerror')
            var self = this;
            var $result = this.$('#o_website_form_result');
			$result.replaceWith(qweb.render("hotel_reservation.status_error_show_msg", {
				responseText : responseText
			}));
        },

	});
});

//Comunicarse con el servidor
