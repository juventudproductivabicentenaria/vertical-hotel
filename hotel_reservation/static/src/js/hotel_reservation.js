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
			'click #searchPerson': '_search_person',
			'click #roomMate_check': '_add_roomMate',
			'click #children_check': '_add_children',
			'click #add_other_children_button': "_add_other_children",
			'click #delete_other_children_button': "_delete_other_children",
			'click #incremento_ninos': '_sumar_ninos',
			'click #desminuir_adults': '_resta_adults',
			'click #desminuir_ninos': '_resta_ninos',
			'click #number_rooms_counter': '_onClickRoomsCounter',
			'click .number_foods_counter': '_onClickFoodsCounter',
			// 'click .checkbox': '_mostrarBoton',
			// 'click .dropdown-menu': '_stop_boton',
			'click #showContainerRoom': '_onClickButtonShowRoom',
			'click #showContainerFood': '_onClickButtonShowFood',
			'change #dateFrom, #date_until': '_onChengeCalendar',
			'click .addFoods': '_onClickAddFoods',
			'click .selectDay': '_onClickSelectDay',
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
			this._addEstructureCategories();
			$("#roomContainer").slideToggle();
			$("#foodContainer").slideToggle();
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

		// _stop_boton: function(event) {
		// 	event.stopPropagation();
		// 	console.log('Stop');
		// 	console.log('Stop');
		// },

		// _mostrarBoton: function (ev){
		// 	var button_reserva = document.getElementById('button_reserva');
	// 		button_reserva.style.display = 'inline';

		// 	var al_menos_uno = false;
		// 	var checkedo = $(".checkbox:checked").length

		// 	if (checkedo >= 1) {
		// 		console.log('Es mayor')
		// 	} else {
		// 		console.log('No es mayor')
		// 		button_reserva.style.display = 'none';
		// 	}
		// },

		_sumar_adults: function (ev){
			var number = Number(document.getElementById("evaluar_adults").value);
			var rooms_available = $('#rooms_available');
			rooms_available.hide();
			var button_reserva = document.getElementById('button_reserva');
			button_reserva.style.display = 'none';
			if (number >=0 && number < 10) {
				number += 1;
				document.getElementById("resultado_adults").innerHTML = eval(number);
				document.getElementById("evaluar_adults").value = number;
				document.getElementById("result_rooms").innerHTML = eval(number);
				document.getElementById("evaluar_rooms").value = number;
			};
		},

		_search_person: function (ev){
			let ci = document.getElementById("identification_VAT").value;
			this._rpc({
				route: '/search_person',
				params: {
					'partner_ci': ci,
				},
			}).then(result => {
				let field_name = document.getElementById("first_last_name_input")
				let field_phone = document.getElementById("phone_input")
				let field_email = document.getElementById("email_input")
				if (result.missing) {
					alert("No se encontraron datos con el documento proporcionado. Por favor, introduzca los datos de la persona manualmente.")
					field_name.value = ""
					field_phone.value = ""
					field_email.value = ""
					field_name.disabled = false
					field_phone.disabled = false
					field_email.disabled = false
				}
				else if (result.no_id) {
					console.log("No CI")
					field_name.value = ""
					field_phone.value = ""
					field_email.value = ""
				}
				else {
					console.log("Good")
					field_name.disabled = true
					field_phone.disabled = true
					field_email.disabled = true
					field_name.value = result.name
					field_phone.value = result.phone
					field_email.value = result.email
				}
			});
		},
		_add_roomMate: function(ev) {
			let container = document.getElementById("container_roomMate")
			let roomMateCheck = document.getElementById("roomMate_check")
			if (!roomMateCheck.checked) {
				container.innerHTML = ""
				return
			}
			container.innerHTML = `<div class="seccion-superior-roomMate mt-3 mb-3">
			<input size="40" id="first_last_name_roomMate_input" type="text" placeholder="Nombre y Apellido" class="form-control ml-4"></input>
			<input id="phone_input_roomMate" type="text" placeholder="Teléfono" class="form-control"></input>
			<input size="40" id="email_input_roomMate" type="text" placeholder="Correo Electrónico" class="form-control ml-4"></input>
		</div>`
		},

		_add_children: function(ev) {
			let container = document.getElementById("container_children")
			let childrenCheck = document.getElementById("children_check")
			if (!childrenCheck.checked) {
				container.innerHTML = ""
				return
			}
			container.innerHTML = `<div id="upper_section" class="seccion-superior-children mt-3 mb-3">
			<input size="40" id="first_last_name_children_input" type="text" placeholder="Nombre y Apellido" class="form-control ml-4 children_input_class""></input>
			<button type="button" id="add_other_children_button" class="ml-2 btn btn-md btn-primary">+ </button>
		</div>`
		},

		_add_other_children: function(ev) {
			let container = document.getElementById("container_children")
			let first_input = document.getElementById("upper_section")
			let deleteButt = document.getElementById("delete_other_children_button")
			if (!deleteButt) {
			first_input.insertAdjacentHTML("beforeend", `<button type="button" id="delete_other_children_button" class="ml-2 btn btn-md btn-primary" >- </button>`)
			}
			container.insertAdjacentHTML("beforeend", `<div class="another_seccion-superior-children mt-3 mb-3">
			<input size="40" type="text" placeholder="Nombre y Apellido" class="form-control ml-4 children_input_class"></input>
		</div>`)
		},

		_delete_other_children: function(ev) {
			console.log("something")
			let container = document.getElementById("container_children")
			console.log(container.childElementCount)
			let deleteButt = document.getElementById("delete_other_children_button")
			if (container.childElementCount == 2) {
				deleteButt.remove()
			}
			container.removeChild(container.lastChild)
		},
		
		_resta_adults: function(ev){
			var number = Number(document.getElementById("evaluar_adults").value);
			var rooms_available = $('#rooms_available');
			var $number_rooms = $("#number_rooms");
			rooms_available.hide();
			var button_reserva = document.getElementById('button_reserva');
			button_reserva.style.display = 'none';
			if (number > 0) {
				number -= 1;
				document.getElementById("resultado_adults").innerHTML = eval(number);
				document.getElementById("evaluar_adults").value = number;
				document.getElementById("result_rooms").innerHTML = eval(number);
				document.getElementById("evaluar_rooms").value = number;
			}
		},

		_onClickRoomsCounter: function (ev){
			var $butoon = $(ev.target).closest('#number_rooms_counter')
			var type = $butoon.data("type");
			var number = Number(document.getElementById("evaluar_rooms").value);
			var limit = Number(document.getElementById("evaluar_adults").value);
			if (number >=0 && number <= 10) {
				if (type =='increase' & number < limit ){
					number += 1;
				}
				if (type =='decrease' &  number > 0 ){
					number -= 1;
				}
				$("#result_rooms").val(number)
				document.getElementById("result_rooms").innerHTML = eval(number);
				document.getElementById("evaluar_rooms").value = number;
			};
		},
		_onClickFoodsCounter: function (ev){
			var self = this;
			var $butoon = $(ev.target).closest('.number_foods_counter')
			var type = $butoon.data("type");
			var food = $butoon.data("food");
			var number = Number(document.getElementById("evaluar_"+food).value);
			var limit = Number(document.getElementById("evaluar_adults").value);
			if (limit == 0){
				var data = {"title": "* La cantidad minima de adultos debe ser  minimo 1."};
				var $error_data = $('#error_data')
				$error_data.show();
				return $error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
			}
			limit += Number(document.getElementById("evaluar_ninos").value);
			if (number >=0 && number <= 15) {
				if (type =='increase' & number < limit ){
					number += 1;
				}
				if (type =='decrease' &  number > 0 ){
					number -= 1;
				}
				$("#result_"+food).val(number)
				document.getElementById("result_"+food).innerHTML = eval(number);
				document.getElementById("evaluar_"+food).value = number;
				
				this._onClickAddFoods(ev,number, food)

			};
		},
		_onClickButtonShowRoom: function (ev){
			$("#roomContainer").slideToggle();
		},
		_onClickButtonShowFood: function (ev) {
			$("#foodContainer").slideToggle();
			this._onChengeCalendar()
		  },

		_onChengeCalendar: function (ev){
			var date_from = $('#dateFrom').val();
			var date_until = $('#date_until').val();
			var fromDate = new Date(date_from + "T00:00:00-04:00");
			var untilDate = new Date(date_until + "T00:00:00-04:00");
			var calendar = $("#calendar");
			calendar.empty();
			// Iterar sobre las fechas y agregarlas al calendario
			var currentDate = new Date(date_from + "T00:00:00-04:00");
			while (currentDate <= untilDate) {
				var day = currentDate.getDate();
				var month = currentDate.getMonth() + 1; // Los meses en JavaScript son indexados desde 0, por lo que se suma 1
				var year = currentDate.getFullYear();
				var order_day = year + '-' + month + '-' + day
				var dayOfWeek = currentDate.getDay();

				// Crear una caja para cada día del calendario
				var id = 'calendar_day_' + day
				var dayBox = $("<div id='" + id + "' data-type='0' data-date='" + order_day + "' class='selectDay'>").text(day);
				var div = $("<div class='container_foods'>");
				var label1 = $("<label class='count_foods evaluar_breakfast'>").text("0")
				var label2 = $("<label class='count_foods evaluar_lunch'>").text("0")
				var label3 = $("<label class='count_foods evaluar_dinner'>").text("0");
				div.append(label1, label2, label3);
				dayBox.append(div);
				if (currentDate < new Date()) {
					dayBox.addClass("past-last");
				}else{
					dayBox.addClass("past-day");
					
				}
				// Agregar la caja al calendario
				calendar.append(dayBox);
				// Avanzar al siguiente día
				currentDate.setDate(currentDate.getDate() + 1);
			}
		},

		_onClickSelectDay: function (ev){
			var $button = $(ev.target).closest('.selectDay')
			var type = $button.data("type");
			if (type == 0){
				$button.data("type", 1);
				$button.addClass("past-day");
			}else{
				$button.data("type", 0);
				$button.removeClass("past-day");
			};
		},
		
		_onClickAddFoods: function (ev,number,food){
			var containers = $('.past-day').map(function(){
				return this;
			}).get();
			$.each(containers, function(index, container) {
				var $container = $(container);
				var $labelFood = $container.find('.evaluar_'+food);
				$labelFood.text(number);
			});
		},
		
		_sumar_ninos: function (ev){
			var number = Number(document.getElementById("evaluar_ninos").value);
			if (number >=0 && number < 5) {
				number += 1;
				document.getElementById("resultado_ninos").innerHTML = eval(number);
				document.getElementById("evaluar_ninos").value = number;
			};
		},

		_resta_ninos: function(ev){
			var number = Number(document.getElementById("evaluar_ninos").value);
			if (number > 0) {
				number -= 1; 
				document.getElementById("resultado_ninos").innerHTML = eval(number);
				document.getElementById("evaluar_ninos").value = number;
			}
		},


	    _onNextBlogClick: function (ev) {
			var date_from = $('#dateFrom').val(); //Para obtener valor de html
			var date_until = $('#date_until').val()
			var adults = $('#evaluar_adults').val()
			var ninos = $('#evaluar_ninos').val()
			var rooms = $('#evaluar_rooms').val()
			var $error_data = $('#error_data')
			var $showContainerRoom = $('#showContainerRoom').prop("checked")
			var $showContainerFood = $('#showContainerFood').prop("checked")
			var self = this;
			$error_data.show();
			if (date_from > date_until) {
				var data = {"title": "* La fecha de salida debe ser mayor que la fecha de llegada."};
				return $error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
			}
			if (adults == 0){
				var data = {"title": "* La cantidad minima de adultos debe ser  minimo 1."};
				return $error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
			}
			if (rooms == 0 && $showContainerRoom){
				var data = {"title": "* La cantidad minima de habitaciones debe ser 1."};
				return $error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
			}
			if (! $showContainerRoom && !$showContainerFood){
				var data = {"title": "* Debe Seleccionar por lo menos un tipo de reservacion."};
				return $error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
			}
			$error_data.hide();
			this._rpc({
				route: '/reservation/search_reservation',
				params: {
					'date_from': date_from,
					'date_until': date_until,
					'adults': adults,
					'ninos': ninos,
					'rooms': rooms,
					'showContainerRoom': $showContainerRoom,
					'showContainerFood': $showContainerFood,
				},
			}).then(result => {
				if (result.error_date) {
					var data = {"title": "* La fecha de llegada debe ser mayor al la fecha actual."};
					return $error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
				}
				self._render_onNextBlogClick(result);
			});
	    },
		_render_onNextBlogClick: function (result) {
			var room = result.rooms_list;
			var service = result.service;
			var $error_data = $('#error_data');
			var rooms_available = $('#rooms_available');

			var button_reserva = document.getElementById('button_reserva');
			$error_data.show();
			rooms_available.show();
			this.rooms_available =  $(qweb._render('hotel_reservation.rooms_available', {
				room: room,
			}));
			this._addEstructureCategories();
			if (room.length > 0 || service) {
				button_reserva.style.display = 'inline';
				var data = {"title": "* Si hay habitaciones disponibles."};
				return $error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));

			}else{
				var data = {"title": "* No hay habitaciones disponibles."};
				return $error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
				
			};
		},


	    _onNextReservar: function (ev) {
			console.log('ButtonReserva')

			var checkbox = $('[name="reserva"]:checked').map(function(){
				return this.value;
			  }).get();

			var containers = $('.selectDay').map(function(){
				return this;
			}).get();
			var date_from = $('#dateFrom').val();
			var date_until = $('#date_until').val();
			var adults = $('#evaluar_adults').val();
			var ninos = $('#evaluar_ninos').val();
			var rooms = $('#evaluar_rooms').val()
			var $showContainerRoom = $('#showContainerRoom').prop("checked")
			var $showContainerFood = $('#showContainerFood').prop("checked")
			var self = this;
			// var fecha =  new Date();
			// var fecha_datefrom =  new Date(date_from);
			// var dia_datefrom = fecha_datefrom.getDate() + 1;
			// var today = fecha.getDate();
			var foodList = [];
			$.each(containers, function(index, container) {
				var $container = $(container);
				var $breakfastLabel = $container.find('.evaluar_breakfast');
				var $dinnerLabel = $container.find('.evaluar_dinner');
				var $lunchLabel = $container.find('.evaluar_lunch');
				var date = $container.data('date')
				var breakfastValue = Number(parseInt($breakfastLabel.text()));
				var dinnerValue = Number(parseInt($dinnerLabel.text()));
				var lunchValue = Number(parseInt($lunchLabel.text()));
				var data = {
					date: date,
					order: [
						{
						quantity: breakfastValue,'code':'DESAYUNO'
					},
						{
						quantity: lunchValue,'code':'ALMUERZO'
					},
						{
						quantity: dinnerValue,'code':'CENA'
					}
				]
					
				};
			
				foodList.push(data);
				
			});
			this._rpc({
				route: '/reservation/reserved_rooms',
				params: {
					'ids': checkbox,
					'date_from': date_from,
					'date_until': date_until,
					'adults': adults,
					'ninos': ninos,
					'rooms': rooms,
					'foodList': foodList,
					'reserve_food': $showContainerFood,
					'reserve_room': $showContainerRoom,
				},
			}).then(data => {
				console.log(data)
				// if (dia_datefrom === today || Number(adults) === 0) {
				if (data.error_validation) {
					self.showerror(data.error_validation);
				}else{
					window.location = '/reserved/' + `${data.reservation_id}`+ '?reserve=True'+'&token='+`${data.token}`
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
