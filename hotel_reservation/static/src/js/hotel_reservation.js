odoo.define('hotel_reservation.ReservationWebsite', function (require) {

	"use strict";

	//alert("Diomedes")

	var publicWidget = require('web.public.widget');

	publicWidget.registry.reservationWebsite = publicWidget.Widget.extend({

		selector: '#reservation', //id

		events: {
			//'click #conteo': '_onNextBlogClick',
			'click #incremento_adults': '_sumar_adults',
			'click #incremento_ninos': '_sumar_ninos',
			'click #desminuir_adults': '_resta_adults',
			'click #desminuir_ninos': '_resta_ninos',
			'click .dropdown-menu': '_stop_boton',
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

	    _onNextBlogClick: function (ev) {

			this.numero +=1

			console.log('numero')
			console.log(numero)

			/*$.get("/reservation/boton_reservation", {
                type: 'popover',
            }).then(function (data) {
				console.log(data)
	    		console.log('Si funciona el server')

                
            });*/

	    	return 

	    },


	});
});

//Comunicarse con el servidor
