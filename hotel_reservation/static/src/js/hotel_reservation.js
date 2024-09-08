odoo.define('hotel_reservation.ReservationWebsite', function (require) {

	"use strict";

	//alert("Diomedes")

	var publicWidget = require('web.public.widget');
	var core = require('web.core');
	var qweb = core.qweb;
	var full_objects = [];
	var adults_counter = 0
	var childrens_counter = 0
	console.log("Perfecto");
	var Dialog = require('web.Dialog');
	// var framework = require('web.framework');

	
	publicWidget.registry.reservationWebsite = publicWidget.Widget.extend({

		selector: '#reservation', //id
		xmlDependencies: ['/hotel_reservation/static/src/xml/search_reservation.xml',
			'/hotel_reservation/static/src/xml/rooms_available.xml',
		],

		events: {
			'click #add_other_person': '__add_other_person',
			'click #busqueda': '_onNextBlogClick',
			'click #reservation_button': '_onNextReservar',
			'click #incremento_adults': '_sumar_adults',
			'click #searchPerson': '_search_person',
			'click #searchRoommate': '_search_roommate',
			'click #roomMate_check': '_add_roomMate',
			'click #children_check': '_add_children',
			'click #add_other_children_button': "_add_other_children",
			'click #delete_other_children_button': "_delete_other_children",
			'click #food_check': '_add_food',
			'click #breakfast_check': '_add_breakfast_date',
			'click #lunch_check': '_add_lunch_date',
			'click #dinner_check': '_add_dinner_date',
			'click #transport_check': '_add_transport',
			'click #room_check': '_add_room',
			'click #origen_select': '_add_origen',
			'click #destino_select': "_add_destino",
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
			let image_menu_foods = $("#image_menu_foods")
			image_menu_foods.hide()
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
		unblockUI: function () {
			const shadowDiv = document.createElement('div');
			shadowDiv.style.position = 'fixed';
			shadowDiv.style.top = '0';
			shadowDiv.style.left = '0';
			shadowDiv.style.width = '100%';
			shadowDiv.style.height = '100%';
			shadowDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.5)'; // color de la sombra con 50% de opacidad
			shadowDiv.style.zIndex = '9999'; // asegura que la sombra esté por encima de todo el contenido
		
			// Agregar el div a la página
			document.body.appendChild(shadowDiv);
		
			// Bloquear la funcionalidad del sitio
			shadowDiv.addEventListener('click', function(event) {
			event.preventDefault(); // prevenir el comportamiento predeterminado de los enlaces
			event.stopPropagation(); // detener la propagación de eventos
			});
				setTimeout(function() {
				// Realizar la acción después de 3 segundos
					window.location.href = '/';
				}, 1000); // 3000 milisegundos equivalen a 3 segundos
		},

		MessageDialog: function (title, content) {
			new Dialog(self,{
				technical: false,
				size:'medium',
				buttons: [
					{
						classes: 'btn bottom-type-1',
						text: "Reservar",
					// 	childrens_counter: function(){
					// 		self._onReservar(ev, true);
					// },
						close: true,
					},
				],
				dialogClass:'col-md-offset-1 col-md-8 text-left',
				title: title,
				$content:qweb.render("hotel_reservation.confirm_data",{
					"content": content
				})
			}).open();
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
				let institution = document.getElementById("institution")
				if (result.missing) {
					alert("No se encontraron datos con el documento proporcionado. Por favor, Introduzca los datos de la persona manualmente.")
					field_name.value = ""
					field_phone.value = ""
					field_email.value = ""
					field_name.disabled = false
					field_phone.disabled = false
					field_email.disabled = false
					institution.disabled = false
				}
				else if (result.no_id) {
					console.log("No CI")
					field_name.value = ""
					field_phone.value = ""
					field_email.value = ""
					institution.value = ""
				}
				else {
					field_name.disabled = true
					field_phone.disabled = true
					field_email.disabled = true
					field_name.value = result.name
					field_phone.value = result.phone
					field_email.value = result.email
					institution.disabled = false
					institution.value = ""
					const first_person = document.getElementById("first_person")
					if (first_person == null) {
					}
					else {
						// first_person.textContent = "Cambió"
					}
				}
			});
		},

		_search_roommate: function(ev) {
			let ci = document.getElementById("identification_VAT_partner").value;
			this._rpc({
				route: '/search_person',
				params: {
					'partner_ci': ci,
				},
			}).then(result => {
				let field_name = document.getElementById("first_last_name_roomMate_input")
				let field_phone = document.getElementById("phone_input_roomMate")
				let field_email = document.getElementById("email_input_roomMate")
				if (result.missing) {
					alert("No se encontraron datos con el documento proporcionado. Por favor, Introduzca los datos de la persona manualmente.")
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
					field_name.disabled = true
					field_phone.disabled = true
					field_email.disabled = true
					field_name.value = result.name
					field_phone.value = result.phone
					field_email.value = result.email
					const first_person = document.getElementById("first_person")
					if (first_person == null) {
					}
					else {
						// first_person.textContent = "Cambió"
					}
				}
			})
		},

		_add_roomMate: function(ev) {
			let container = document.getElementById("container_roomMate")
			let container_row = document.getElementById("row_partner_div")
			let roomMateCheck = document.getElementById("roomMate_check")
			if (!roomMateCheck.checked) {
				document.getElementById("identification_VAT_partner").remove();
				document.getElementById("searchRoommate").remove()
				container.innerHTML = ""
				return
			}
			container.r
			const input = document.createElement("input")
			input.id = "identification_VAT_partner"
			input.type = "text"
			input.placeholder = "Cédula de Identidad o RIF"
			input.oninput = "this.value = this.value.replace(/[^0-9]/g, '')"
			input.classList.add("form-control", "mt-4", "ml-4")

			const button = document.createElement("button");
			button.type = "button";
			button.id = "searchRoommate";
			button.classList.add("btn", "bottom-type-1", "ml-3", "mt-4");
			button.textContent = "Buscar";
			
			container.innerHTML = `
			<div class="seccion-superior-roomMate row m-4">
				<input size="40" id="first_last_name_roomMate_input" disabled="true" type="text" placeholder="Nombre y Apellido" class="form-control"></input>
				<input id="phone_input_roomMate" type="text" disabled="true" placeholder="Teléfono" class="form-control"></input>
				<input size="40" id="email_input_roomMate" disabled="true" type="text" placeholder="Correo Electrónico" class="form-control"></input>
			</div>`
			container_row.prepend(button);
			container_row.prepend(input);
		},

		_add_children: function(ev) {
			let container = document.getElementById("container_children")
			let childrenCheck = document.getElementById("children_check")
			if (!childrenCheck.checked) {
				container.innerHTML = ""
				return
			}
			container.innerHTML = `
			<div id="upper_section" class="seccion-superior-children row mb-1">
				<input size="40" id="first_last_name_children_input" type="text" placeholder="Nombre y Apellido" class="form-control children_input_class""></input>
				<input id="phone_children" type="text" style="display: none;" placeholder="Cédula de Identidad" class="form-control children_phone_class"></input>
				<button type="button" id="add_other_children_button" class="ml-2 btn bottom-type-1">+ </button>
			</div>`
		},

		_add_other_children: function(ev) {
			let container = document.getElementById("container_children")
			let first_input = document.getElementById("upper_section")
			let deleteButt = document.getElementById("delete_other_children_button")
			if (!deleteButt) {
			first_input.insertAdjacentHTML("beforeend", `
				<button type="button" id="delete_other_children_button" class="ml-2 btn bottom-type-1" >- </button>`)
			}
			container.insertAdjacentHTML("beforeend", `
			<div class="another_seccion-superior-children row mb-1">
				<input size="40" type="text" placeholder="Nombre y Apellido" class="form-control children_input_class"></input>
				<input id="phone_children" style="display: none;" type="text" placeholder="Cédula de Identidad" class="form-control children_phone_class"></input>
			</div>`)
		},

		_delete_other_children: function(ev) {
			let container = document.getElementById("container_children")
			let deleteButt = document.getElementById("delete_other_children_button")
			if (container.childElementCount == 2) {
				deleteButt.remove()
			}
			container.removeChild(container.lastChild)
		},

		_add_food: function(ev) {
			let self = this;
			let container = document.getElementById("breakfast_container")
			let image_menu_foods = $("#image_menu_foods")
			image_menu_foods.show()
			let check = document.getElementById("food_check")
			if (!check.checked) {
				container.innerHTML = ""
				var data = {"image_data":false }
				image_menu_foods.replaceWith(qweb.render("hotel_reservation.image_menu_foods",
					data
				));
				return
			}
			container.innerHTML = `<div class="container">
			<div class="row justify-content-around">
				<div class="col-sm-3 m-2 border border-primary" style="border-radius: 20px;">
					<ul class="list-group mb-3 mt-3">
						<li class="list-group-item d-flex align-items-center bg-secondary text-light border border-primary">
							<label class="form-check-label mr-2" for="breakfast_check">Desayuno</label>
							<input value="Desayuno" class="form-check-input" type="checkbox" id="breakfast_check">
						</li>
						<div id="breakfast_date_container" class="d-flex align-items-center "></div>
					</ul>
				</div>
		
				<div class="col-sm-3 m-2 border border-primary" style="border-radius: 20px;">
					<ul class="list-group mb-3 mt-3">
						<li class="list-group-item d-flex align-items-center bg-secondary text-light border border-primary">
							<label class="form-check-label mr-2" for="lunch_check">Almuerzo</label>
							<input value="Almuerzo" class="form-check-input" type="checkbox" id="lunch_check">
						</li>
						<div id="lunch_date_container" class="d-flex align-items-center "></div>
					</ul>
				</div>
		
				<div class="col-sm-3 m-2 border border-primary" style="border-radius: 20px;">
					<ul class="list-group mb-3 mt-3">
						<li class="list-group-item d-flex align-items-center bg-secondary text-light border border-primary">
							<label class="form-check-label mr-2" for="dinner_check">Cena</label>
							<input value="Cena" class="form-check-input" type="checkbox" id="dinner_check">
						</li>
						<div id="dinner_date_container" class="d-flex align-items-center"></div>
					</ul>
				</div>
			</div>
		</div>`
		var date_from = $('#dateFrom').val();
		var date_until = $('#date_until').val()
		this._rpc({
			route: '/reservation/search_menu_foods',
			params: {
				'date_from': date_from,
				'date_until': date_until,
			},
		}).then(result => {
			// self.unblockUI(ev);
			console.log(result)
			console.log(result.image_data)
			
			if (result.image_data) {
				var data ={
					"image_data":result.image_data
				}
				image_menu_foods.replaceWith(qweb.render("hotel_reservation.image_menu_foods",
					data
				));
			};
		});
		},

		_add_breakfast_date: function(ev) {
			let container = document.getElementById("breakfast_date_container")
			let date_since = document.getElementById("dateFrom")
			let date_to = document.getElementById("date_until")
			const endDate = new Date(date_to.value);
			const oneDayInMilliseconds = 1000 * 60 * 60 * 24;
			const newEndDate = new Date(endDate.getTime() + oneDayInMilliseconds);
			let check = document.getElementById("breakfast_check")
			if (!check.checked) {
				container.innerHTML = ""
				return
			}
			container.innerHTML = `
			
			<div class="mt-2">
				<span class="text-type-1" for="breakfastDate">Fechas para desayunar</span>
				<input type="text" class="border rounded p-2" id="breakfastDate" name="request_breakfast_date_from" required="1"/>
			</div>
			`
			$(document).ready(function() {
				$('#breakfastDate').datepicker({
					startDate: new Date(),
					endDate: newEndDate,
					multidate: true,
					format: "dd/mm/yyyy",
					daysOfWeekHighlighted: "5,6",
					language: 'es',
				})
			});


		},
		_add_lunch_date: function(ev) {
			let container = document.getElementById("lunch_date_container")
			let date_since = document.getElementById("dateFrom")
			let date_to = document.getElementById("date_until")
			const endDate = new Date(date_to.value);
			const oneDayInMilliseconds = 1000 * 60 * 60 * 24;
			const newEndDate = new Date(endDate.getTime() + oneDayInMilliseconds);
			let check = document.getElementById("lunch_check")
			if (!check.checked) {
				container.innerHTML = ""
				return
			}
			container.innerHTML = `
			<div class="mt-2">
				<span class="text-type-1" for="lunchDate">Fechas para Almorzar</span>
				<input type="text" class="border rounded p-2" id="lunchDate" name="request_lunch_date_from" required="1"/>
			</div>
			`
			$(document).ready(function() {
				$('#lunchDate').datepicker({
					startDate: new Date(),
					endDate: newEndDate,
					multidate: true,
					format: "dd/mm/yyyy",
					daysOfWeekHighlighted: "5,6",
					language: 'es',
				})
			});
		},
		_add_dinner_date: function(ev) {
			let container = document.getElementById("dinner_date_container")
			let date_since = document.getElementById("dateFrom")
			let date_to = document.getElementById("date_until")
			let check = document.getElementById("dinner_check")
			if (!check.checked) {
				container.innerHTML = ""
				return
			}
			container.innerHTML = `
			<div class="mt-2">
				<span class="text-type-1" for="dinnerDate">Fechas para Cenar</span>
				<input type="text" class="border rounded p-2" id="dinnerDate" name="request_breakfast_date_from" required="1"/>
			</div>
			`
			$(document).ready(function() {
				$('#dinnerDate').datepicker({
					startDate: new Date(),
					endDate: new Date(date_to.value),
					multidate: true,
					format: "dd/mm/yyyy",
					daysOfWeekHighlighted: "5,6",
					language: 'es',
				})
			});
		},

		_add_room: function(ev) {
			let counter = document.getElementById("counterRooms")
			let num = parseInt(counter.textContent); 
			let result = num + 1;
			let before = num - 1;
			let check = document.getElementById("room_check")
			if (!check.checked) {
				counter.textContent = before.toString() + " Habitaciones"
				return
			}
			counter.textContent = result.toString() + " Habitaciones"
		},

		_add_origen: function(ev) {
			const estados = [
				"Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar", "Carabobo",
				"Cojedes", "Delta Amacuro", "Dependencias Federales", "Distrito Federal", "Falcón",
				"Guárico", "Lara", "Mérida", "Miranda", "Monagas", "Nueva Esparta", "Portuguesa",
				"Sucre", "Táchira", "Trujillo", "Vargas", "Yaracuy", "Zulia"
			];
		
			const select = document.getElementById("origen_select");
			if (select.children.length > 1) {
				return
			}
			estados.forEach(estado => {
				const option = document.createElement("option");
				option.text = estado;
				select.add(option);
			});
		},
		_add_destino: function(ev) {
			const estados = [
				"Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar", "Carabobo",
				"Cojedes", "Delta Amacuro", "Dependencias Federales", "Distrito Federal", "Falcón",
				"Guárico", "Lara", "Mérida", "Miranda", "Monagas", "Nueva Esparta", "Portuguesa",
				"Sucre", "Táchira", "Trujillo", "Vargas", "Yaracuy", "Zulia"
			];
		
			const select = document.getElementById("destino_select");
			if (select.children.length > 1) {
				return
			}
			estados.forEach(estado => {
				const option = document.createElement("option");
				option.text = estado;
				select.add(option);
			});
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

		_add_transport: function(ev) {
			let container = document.getElementById("container_transport")
			let check = document.getElementById("transport_check")
			if (!check.checked) {
				container.innerHTML = ""
				return
			}
			container.innerHTML = `
			<div class="border bg-light ml-3 mb-4 text-center" style="width: 100px; height: 30px;">
                        Origen
                        <select id="origen_select" class="mt-3 w-100">
                            <option>
                                Amazonas
                            </option>
                        </select>
                    </div>
                    <div class="border bg-light ml-3 mb-4 text-center" style="width: 100px; height: 30px;">
                        Destino
                        <select id="destino_select" class="mt-3 w-100">
                            <option>
                                Amazonas
                            </option>
                        </select>
                    </div>
			`
		},

		__add_other_person: function(ev) {
			let self = this;
			self.verificationDataError(ev);
			var $error_data = $("#error_data")
			$error_data.hide();
			var error = this.verificationDataError(ev);
			if (error) {
				$error_data.show();
				return
			}
			let ci = document.getElementById("identification_VAT").value
			let field_name = document.getElementById("first_last_name_input").value
			let field_phone = document.getElementById("phone_input").value
			let field_email = document.getElementById("email_input").value
			try {
				var ci_part = document.getElementById("identification_VAT_partner").value
	
				var field_name_part = document.getElementById("first_last_name_roomMate_input").value
				var field_phone_part = document.getElementById("phone_input_roomMate").value
				var field_email_part = document.getElementById("email_input_roomMate").value
			} catch(e){
				var ci_part = ""
	
				var field_name_part = ""
				var field_phone_part = ""
				var field_email_part = ""
			}
			const institution = document.getElementById("institution")
			document.getElementById("par_list_persons").classList.remove("d-none")

			const listaPadre = document.getElementById('list_ppl')
			var childrens = document.getElementById("container_children").children.length
			let html_children = document.getElementsByClassName("children_input_class")
			let html_children_phone = document.getElementsByClassName("children_phone_class")
			var children_objects = [];
			var include_room = document.getElementById("room_check").checked
			function delete_data_form() {
				let form = document.getElementById("search_reservation_form")
				let roomMate_check = document.getElementById("roomMate_check")
				let children_check = document.getElementById("children_check")
				let food_checked = document.getElementById("food_check")
				if (roomMate_check.checked) {
					roomMate_check.click()
				}
				if (children_check.checked) {
					children_check.click()
				}
				if (food_checked.checked) {
					food_checked.click()
				}
				const date_from_before = document.getElementById("dateFrom").value
				const date_until_before = document.getElementById("date_until").value
				form.reset()

				document.getElementById("dateFrom").value = date_from_before
				document.getElementById("date_until").value = date_until_before
				
				document.getElementById("dateFrom").disabled = true;
				document.getElementById("date_until").disabled = true
			}
			if (html_children) {
				const childrenArray = Array.from(html_children);
				const childrenPhoneArray = Array.from(html_children_phone);


				for (let i = 0; i < childrenArray.length; i++) {
					const nombre = childrenArray[i].value;
					const vat = childrenPhoneArray[i].value;
					console.log(nombre)
					const objeto = {
						nombre,
						vat,
					};

					children_objects.push(objeto);
				}
			}
			const add_food = document.getElementById("food_check").checked
			const add_transport = document.getElementById("transport_check").checked
			if (add_transport) {
				var origen = document.getElementById("origen_select").value;
				var destiny = document.getElementById("destino_select").value;
			}
			else {
				origen = ""
				destiny = ""
			}
			if (add_food) {
				let breakfast = document.getElementById("breakfast_check").checked
				let lunch = document.getElementById("lunch_check").checked
				let dinner = document.getElementById("dinner_check").checked
				if (breakfast && lunch && dinner) {
					let from_break = document.getElementById("breakfastDate").value
					let from_lunch = document.getElementById("lunchDate").value
					let from_dinner = document.getElementById("dinnerDate").value

					const breakfast_dict = {
						"from_break": from_break}
						
					
					const lunch_dict = {
						"from_lunch": from_lunch}
					
					const dinner_dict = {
						"from_dinner": from_dinner}
					
					const ready_to_insert = {
						"vat": ci,
						"name": field_name,
						"phone": field_phone,
						"email": field_email,
						"second_vat": ci_part,
						"second_name": field_name_part,
						"second_phone": field_phone_part,
						"second_email": field_email_part,
						"childrens": children_objects,
						"include_room": include_room,
						"include_food": true,
						"breakfast": breakfast_dict,
						"lunch": lunch_dict,
						"dinner": dinner_dict,
						"include_transport": add_transport,
						"origen": origen,
						"destiny": destiny,
						'institution_name': institution.value,
					}
					full_objects.push(ready_to_insert)
					children_objects = []
				}
				

				else if (breakfast && lunch && !dinner) {
					let from_break = document.getElementById("breakfastDate").value
					let from_lunch = document.getElementById("lunchDate").value
					const breakfast_dict = {
						"from_break": from_break}
						
					
					const lunch_dict = {
						"from_lunch": from_lunch}
					
					
					const ready_to_insert = {
						"vat": ci,
						"name": field_name,
						"phone": field_phone,
						"email": field_email,
						"second_vat": ci_part,
						"second_name": field_name_part,
						"second_phone": field_phone_part,
						"second_email": field_email_part,
						"childrens": children_objects,
						"include_room": include_room,
						"include_food": true,
						"breakfast": breakfast_dict,
						"lunch": lunch_dict,
						"include_transport": add_transport,
						"origen": origen,
						"destiny": destiny,
						'institution_name': institution.value,
					}
					full_objects.push(ready_to_insert)
					children_objects = []
				}

				else if (breakfast && !lunch && !dinner) {
					let from_break = document.getElementById("breakfastDate").value
					const breakfast_dict = {
						"from_break": from_break}
						

					const ready_to_insert = {
						"vat": ci,
						"name": field_name,
						"phone": field_phone,
						"email": field_email,
						"second_vat": ci_part,
						"second_name": field_name_part,
						"second_phone": field_phone_part,
						"second_email": field_email_part,
						"childrens": children_objects,
						"include_room": include_room,
						"include_food": true,
						"breakfast": breakfast_dict,
						"include_transport": add_transport,
						"origen": origen,
						"destiny": destiny,
						'institution_name': institution.value,
					}
					full_objects.push(ready_to_insert)
					children_objects = []
				}

				else if (!breakfast && lunch && !dinner) {
					let from_lunch = document.getElementById("lunchDate").value

					const lunch_dict = {
						"from_lunch": from_lunch}
						

					const ready_to_insert = {
						"vat": ci,
						"name": field_name,
						"phone": field_phone,
						"email": field_email,
						"second_vat": ci_part,
						"second_name": field_name_part,
						"second_phone": field_phone_part,
						"second_email": field_email_part,
						"childrens": children_objects,
						"include_room": include_room,
						"include_food": true,
						"lunch": lunch_dict,
						"include_transport": add_transport,
						"origen": origen,
						"destiny": destiny,
						'institution_name': institution.value,
					}
					full_objects.push(ready_to_insert)
					children_objects = []
				}

				else if (!breakfast && !lunch && dinner) {
					let from_dinner = document.getElementById("dinnerDate").value

					const dinner_dict = {
						"from_dinner": from_dinner}
						

					const ready_to_insert = {
						"vat": ci,
						"name": field_name,
						"phone": field_phone,
						"email": field_email,
						"second_vat": ci_part,
						"second_name": field_name_part,
						"second_phone": field_phone_part,
						"second_email": field_email_part,
						"childrens": children_objects,
						"include_room": include_room,
						"include_food": true,
						"dinner": dinner_dict,
						"include_transport": add_transport,
						"origen": origen,
						"destiny": destiny,
						'institution_name': institution.value,
					}
					full_objects.push(ready_to_insert)
					children_objects = []
				}

				else if (breakfast && !lunch && dinner) {
					let from_break = document.getElementById("breakfastDate").value
					let from_dinner = document.getElementById("dinnerDate").value

					const breakfast_dict = {
						"from_break": from_break}
					
					const dinner_dict = {
						"from_dinner": from_dinner}

					const ready_to_insert = {
						"vat": ci,
						"name": field_name,
						"phone": field_phone,
						"email": field_email,
						"second_vat": ci_part,
						"second_name": field_name_part,
						"second_phone": field_phone_part,
						"second_email": field_email_part,
						"childrens": children_objects,
						"include_room": include_room,
						"include_food": true,
						"breakfast": breakfast_dict,
						"dinner": dinner_dict,
						"include_transport": add_transport,
						"origen": origen,
						"destiny": destiny,
						'institution_name': institution.value,
					}
					full_objects.push(ready_to_insert)
					children_objects = []
				}

				else if (!breakfast && lunch && dinner) {
					let from_lunch = document.getElementById("lunchDate").value
					let from_dinner = document.getElementById("dinnerDate").value
					
					const lunch_dict = {
						"from_lunch": from_lunch}
					
					const dinner_dict = {
						"from_dinner": from_dinner}
					
					const ready_to_insert = {
						"vat": ci,
						"name": field_name,
						"phone": field_phone,
						"email": field_email,
						"second_vat": ci_part,
						"second_name": field_name_part,
						"second_phone": field_phone_part,
						"second_email": field_email_part,
						"childrens": children_objects,
						"include_room": include_room,
						"include_food": true,
						"lunch": lunch_dict,
						"dinner": dinner_dict,
						"include_transport": add_transport,
						"origen": origen,
						"destiny": destiny,
						'institution_name': institution.value,
					}
					full_objects.push(ready_to_insert)
					children_objects = []
				}

			}
			else {
				const ready_to_insert = {
					"vat": ci,
					"name": field_name,
					"phone": field_phone,
					"email": field_email,
					"second_vat": ci_part,
					"second_name": field_name_part,
					"second_phone": field_phone_part,
					"second_email": field_email_part,
					"childrens": children_objects,
					"include_food": false,
					"include_room": include_room,
					"include_transport": add_transport,
					"origen": origen,
					"destiny": destiny,
					'institution_name': institution.value,
				}
				full_objects.push(ready_to_insert)
				children_objects = []
			}


			if (ci_part && childrens > 0) {
				const nuevoElementoLi = document.createElement('li');
				nuevoElementoLi.textContent = field_name + " (Acompañante: " + field_name_part + "), " + "(Niños: " + childrens + ")";
				nuevoElementoLi.classList.add('fade');

				// Agregar la clase 'show' después de un breve retraso para hacer que el elemento aparezca gradualmente
				listaPadre.appendChild(nuevoElementoLi);
				setTimeout(function() {
					nuevoElementoLi.classList.add('show');
				}, 100);
				adults_counter += 2
				childrens_counter = childrens + childrens_counter
			}
			else if (ci_part && childrens == 0) {
				const nuevoElementoLi = document.createElement('li');
				nuevoElementoLi.textContent = field_name + " (Acompañante: " + field_name_part + ")";
				nuevoElementoLi.classList.add('fade');

				// Agregar la clase 'show' después de un breve retraso para hacer que el elemento aparezca gradualmente
				listaPadre.appendChild(nuevoElementoLi);
				setTimeout(function() {
					nuevoElementoLi.classList.add('show');
				}, 100);
				adults_counter += 2
				childrens_counter = childrens + childrens_counter
			}
			else if (childrens > 0 && !ci_part) {
				const nuevoElementoLi = document.createElement('li');
				nuevoElementoLi.textContent = field_name + " (Niños: " + childrens + ")";
				nuevoElementoLi.classList.add('fade');

				// Agregar la clase 'show' después de un breve retraso para hacer que el elemento aparezca gradualmente
				listaPadre.appendChild(nuevoElementoLi);
				setTimeout(function() {
					nuevoElementoLi.classList.add('show');
				}, 100);
				childrens_counter = childrens + childrens_counter
			}
			else if (childrens == 0 && !ci_part) {
				const nuevoElementoLi = document.createElement('li');
				nuevoElementoLi.textContent = field_name;
				nuevoElementoLi.classList.add('fade');

				// Agregar la clase 'show' después de un breve retraso para hacer que el elemento aparezca gradualmente
				listaPadre.appendChild(nuevoElementoLi);
				setTimeout(function() {
					nuevoElementoLi.classList.add('show');
				}, 100);
			}

			delete_data_form()

		},

		verificationDataError: function (ev) {
			var self = this;
			var identification_vat = $('#identification_VAT').val()
			var first_last_name_input = $('#first_last_name_input').val()
			var phone_input = $('#phone_input').val()
			var email_input = $('#email_input').val()
			var room_check = $('#room_check').is(':checked')
			var food_check = $('#food_check').is(':checked')
		
			var $error_data = $('#error_data')
			if (identification_vat == null || identification_vat == undefined || identification_vat == '') {
				var data = {"title": "* Por favor, Introduzca la Cédula de Identidad / RIF."};
				$error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
				return true
			}
			if (first_last_name_input == null || first_last_name_input == undefined || first_last_name_input == '') {
				var data = {"title": "* Por favor, Introduzca el Nombre y Apellido."};
				$error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
				return true
			}
			if (phone_input == null || phone_input == undefined || phone_input == '') {
				var data = {"title": "* Por favor, Introduzca el teléfono."};
				$error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
				return true
			}
			if (email_input == null || email_input == undefined || email_input == '') {
				var data = {"title": "* Por favor, Introduzca el correo electrónico."};
				$error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
				return true
			}
			if (room_check == null && food_check == null || room_check == false && food_check == false) {
				var data = {"title": "* Por favor, Seleccione al menos una opción de Comida o Habitación."};
				$error_data.replaceWith(qweb.render("hotel_reservation.error_data",data));
				return true
			}
			return false
		},
		_onNextBlogClick: function (ev) {
			var self = this;
			var $error_data = $('#error_data')
			$error_data.hide();
			var error = this.verificationDataError(ev);
			if (error) {
				$error_data.show();
				return
			}
			self._onReservar(ev, true);
		},

	    _onReservar: function (ev, respuesta) {
			var self = this;
			// var respuesta = confirm("Por favor, presione OK solo cuando esté seguro de que desea realizar la reservación.");
			if (respuesta) {
				// Ejecutar la acción si el usuario hace clic en "Aceptar"
				let first_last_name_input = document.getElementById("first_last_name_input")
				
			var date_from = $('#dateFrom').val();
			var date_until = $('#date_until').val()
			let counterRooms = document.getElementById("counterRooms")
			
			if (full_objects.length > 0) {
				if (first_last_name_input.value != "") {
					document.getElementById("add_other_person").click()
				}

				this._rpc({
					route: '/reservation/search_reservation',
					params: {
						'full_data': full_objects,
						'date_from': date_from,
						'date_until': date_until,
						'adults': adults_counter,
						'ninos': childrens_counter
					},
				}).then(result => {
					self.unblockUI(ev);
					if (result.error_validation) {
						self.MessageDialog(result.title_error, result.content_error)
						return
					};
					if (result.reserved){
						window.location = '/reserved/' + `${result.reservation_id}`+ '?reserve=True'+'&token='+`${result.token}`
					}
				});
				return
			}

			let list_of_names = []
			let list_of_cis = []
			let list_of_phones = []
			let list_of_emails = []

			var childrens = document.getElementById("container_children").children.length
			let html_children = document.getElementsByClassName("children_input_class")
			let html_children_phone = document.getElementsByClassName("children_phone_class")
			const children_objects = [];
			if (html_children) {
				const childrenArray = Array.from(html_children);
				const childrenPhoneArray = Array.from(html_children_phone);


				for (let i = 0; i < childrenArray.length; i++) {
					console.log(childrenArray.length)
					const nombre = childrenArray[i].value;
					const vat = childrenPhoneArray[i].value;

					const objeto = {
						nombre,
						vat,
					};
					console.log(objeto)
					children_objects.push(objeto);
				}
			}
			

			if (childrens == null) {
				childrens = 0
			}
			let num_rooms = parseInt(counterRooms.textContent);

			let main_ci = document.getElementById("identification_VAT")
			list_of_cis.push(main_ci.value)

			list_of_names.push(first_last_name_input.value)

			let main_phone = document.getElementById("phone_input")
			list_of_phones.push(main_phone.value)

			let main_email = document.getElementById("email_input")
			list_of_emails.push(main_email.value)

			let institution = document.getElementById("institution")

			let first_last_name_roomMate_input = document.getElementById("first_last_name_roomMate_input")
			
			let second_ci = document.getElementById("identification_VAT_partner")

			let second_phone = document.getElementById("phone_input_roomMate")

			let second_email = document.getElementById("email_input_roomMate")

			var has_partner = false
			var adults = 0
			if (first_last_name_input.value != "") {
				adults += 1
			}
			if (first_last_name_roomMate_input != null) {
				adults += 1
				list_of_names.push(first_last_name_roomMate_input.value)
				list_of_cis.push(second_ci.value)
				list_of_phones.push(second_phone.value)
				list_of_emails.push(second_email.value)
				has_partner = true
			}
			const include_room = document.getElementById("room_check").checked

			const add_food = document.getElementById("food_check").checked
			const add_transport = document.getElementById("transport_check").checked
			if (add_transport) {
				var origen = document.getElementById("origen_select").value;
				var destiny = document.getElementById("destino_select").value;
				console.log(origen)
				console.log(destiny)
			}
			else {
				origen = ""
				destiny = ""
			}
			if (add_food) {
				let breakfast = document.getElementById("breakfast_check").checked
				let lunch = document.getElementById("lunch_check").checked
				let dinner = document.getElementById("dinner_check").checked
				if (breakfast && lunch && dinner) {
					let from_break = document.getElementById("breakfastDate").value
					let from_lunch = document.getElementById("lunchDate").value
					let from_dinner = document.getElementById("dinnerDate").value

					const breakfast_dict = {
						"from_break": from_break}
						
					
					const lunch_dict = {
						"from_lunch": from_lunch}
					
					const dinner_dict = {
						"from_dinner": from_dinner}
	
					this._rpc({
						route: '/reservation/search_reservation',
						params: {
							'children_list': children_objects,
							'has_partner': has_partner,
							'rooms': num_rooms,
							'names': list_of_names,
							'vats': list_of_cis,
							'emails': list_of_emails,
							'phones': list_of_phones,
							'institution_name': institution.value,
							'date_from': date_from,
							'date_until': date_until,
							'adults': adults,
							'ninos': childrens,
							'rooms': num_rooms,
							'include_room': include_room,
							'include_food': true,
							"breakfast": breakfast_dict,
							"lunch": lunch_dict,
							"dinner": dinner_dict,
							"include_transport": add_transport,
							"origen": origen,
							"destiny": destiny,
							'showContainerRoom': document.getElementById('room_check').checked,
							'showContainerFood': document.getElementById('food_check').checked,
						},
					}).then(result => {
						self.unblockUI(ev);
						if (result.error_validation) {
							self.MessageDialog(result.title_error, result.content_error)
							return
						};
						if (result.reserved){
							window.location = '/reserved/' + `${result.reservation_id}`+ '?reserve=True'+'&token='+`${result.token}`
						}
					});
				}
				

				else if (breakfast && lunch && !dinner) {
					let from_break = document.getElementById("breakfastDate").value
					let from_lunch = document.getElementById("lunchDate").value
					const breakfast_dict = {
						"from_break": from_break}

					const lunch_dict = {
						"from_lunch": from_lunch}
	
					this._rpc({
						route: '/reservation/search_reservation',
						params: {
							'children_list': children_objects,
							'has_partner': has_partner,
							'rooms': num_rooms,
							'names': list_of_names,
							'vats': list_of_cis,
							'emails': list_of_emails,
							'phones': list_of_phones,
							'institution_name': institution.value,
							'date_from': date_from,
							'date_until': date_until,
							'adults': adults,
							'ninos': childrens,
							'rooms': num_rooms,
							'include_room': include_room,
							'include_food': true,
							"breakfast": breakfast_dict,
							"lunch": lunch_dict,
							"include_transport": add_transport,
							"origen": origen,
							"destiny": destiny,
							'showContainerRoom': document.getElementById('room_check').checked,
							'showContainerFood': document.getElementById('food_check').checked,
						},
					}).then(result => {
						self.unblockUI(ev);
						if (result.error_validation) {
							self.MessageDialog(result.title_error, result.content_error)
							return
						};
						if (result.reserved){
							window.location = '/reserved/' + `${result.reservation_id}`+ '?reserve=True'+'&token='+`${result.token}`
						}
					});
					
				}

				else if (breakfast && !lunch && !dinner) {
					let from_break = document.getElementById("breakfastDate").value
					const breakfast_dict = {
						"from_break": from_break}
	
					this._rpc({
						route: '/reservation/search_reservation',
						params: {
							'children_list': children_objects,
							'has_partner': has_partner,
							'rooms': num_rooms,
							'names': list_of_names,
							'vats': list_of_cis,
							'emails': list_of_emails,
							'phones': list_of_phones,
							'institution_name': institution.value,
							'date_from': date_from,
							'date_until': date_until,
							'adults': adults,
							'ninos': childrens,
							'rooms': num_rooms,
							'include_room': include_room,
							'include_food': true,
							"breakfast": breakfast_dict,
							"include_transport": add_transport,
							"origen": origen,
							"destiny": destiny,
							'showContainerRoom': document.getElementById('room_check').checked,
							'showContainerFood': document.getElementById('food_check').checked,
						},
					}).then(result => {
						self.unblockUI(ev);
						if (result.error_validation) {
							self.MessageDialog(result.title_error, result.content_error)
							return
						};
						if (result.reserved){
							window.location = '/reserved/' + `${result.reservation_id}`+ '?reserve=True'+'&token='+`${result.token}`
						}
					});
						
				}

				else if (!breakfast && lunch && !dinner) {
					let from_lunch = document.getElementById("lunchDate").value

					const lunch_dict = {
						"from_lunch": from_lunch}
	
					this._rpc({
						route: '/reservation/search_reservation',
						params: {
							'children_list': children_objects,
							'has_partner': has_partner,
							'rooms': num_rooms,
							'names': list_of_names,
							'vats': list_of_cis,
							'emails': list_of_emails,
							'phones': list_of_phones,
							'institution_name': institution.value,
							'date_from': date_from,
							'date_until': date_until,
							'adults': adults,
							'ninos': childrens,
							'rooms': num_rooms,
							'include_room': include_room,
							'include_food': true,
							"lunch": lunch_dict,
							"include_transport": add_transport,
							"origen": origen,
							"destiny": destiny,
							'showContainerRoom': document.getElementById('room_check').checked,
							'showContainerFood': document.getElementById('food_check').checked,
						},
					}).then(result => {
						self.unblockUI(ev);
						if (result.error_validation) {
							self.MessageDialog(result.title_error, result.content_error)
							return
						};
						if (result.reserved){
							window.location = '/reserved/' + `${result.reservation_id}`+ '?reserve=True'+'&token='+`${result.token}`
						}
					});
						
				}

				else if (!breakfast && !lunch && dinner) {
					let from_dinner = document.getElementById("dinnerDate").value
					const dinner_dict = {
						"from_dinner": from_dinner}
	
					this._rpc({
						route: '/reservation/search_reservation',
						params: {
							'children_list': children_objects,
							'has_partner': has_partner,
							'rooms': num_rooms,
							'names': list_of_names,
							'vats': list_of_cis,
							'emails': list_of_emails,
							'phones': list_of_phones,
							'institution_name': institution.value,
							'date_from': date_from,
							'date_until': date_until,
							'adults': adults,
							'ninos': childrens,
							'rooms': num_rooms,
							'include_room': include_room,
							'include_food': true,
							"dinner": dinner_dict,
							"include_transport": add_transport,
							"origen": origen,
							"destiny": destiny,
							'showContainerRoom': document.getElementById('room_check').checked,
							'showContainerFood': document.getElementById('food_check').checked,
						},
					}).then(result => {
						self.unblockUI(ev);
						if (result.error_validation) {
							self.MessageDialog(result.title_error, result.content_error)
							return
						};
						if (result.reserved){
							window.location = '/reserved/' + `${result.reservation_id}`+ '?reserve=True'+'&token='+`${result.token}`
						}
					});
						
				}

				else if (breakfast && !lunch && dinner) {
					let from_break = document.getElementById("breakfastDate").value
					let from_dinner = document.getElementById("dinnerDate").value

					const breakfast_dict = {
						"from_break": from_break}
					
					const dinner_dict = {
						"from_dinner": from_dinner}
	
					this._rpc({
						route: '/reservation/search_reservation',
						params: {
							'children_list': children_objects,
							'has_partner': has_partner,
							'rooms': num_rooms,
							'names': list_of_names,
							'vats': list_of_cis,
							'emails': list_of_emails,
							'phones': list_of_phones,
							'institution_name': institution.value,
							'date_from': date_from,
							'date_until': date_until,
							'adults': adults,
							'ninos': childrens,
							'rooms': num_rooms,
							'include_room': include_room,
							'include_food': true,
							"breakfast": breakfast_dict,
							"dinner": dinner_dict,
							"include_transport": add_transport,
							"origen": origen,
							"destiny": destiny,
							'showContainerRoom': document.getElementById('room_check').checked,
							'showContainerFood': document.getElementById('food_check').checked,
						},
					}).then(result => {
						self.unblockUI(ev);
						if (result.error_validation) {
							self.MessageDialog(result.title_error, result.content_error)
							return
						};
						if (result.reserved){
							window.location = '/reserved/' + `${result.reservation_id}`+ '?reserve=True'+'&token='+`${result.token}`
						}
					});

				}

				else if (!breakfast && lunch && dinner) {
					let from_lunch = document.getElementById("lunchDate").value

					let from_dinner = document.getElementById("dinnerDate").value

					const lunch_dict = {
						"from_lunch": from_lunch}
					
					const dinner_dict = {
						"from_dinner": from_dinner}

					this._rpc({
						route: '/reservation/search_reservation',
						params: {
							'children_list': children_objects,
							'has_partner': has_partner,
							'rooms': num_rooms,
							'names': list_of_names,
							'vats': list_of_cis,
							'emails': list_of_emails,
							'phones': list_of_phones,
							'institution_name': institution.value,
							'date_from': date_from,
							'date_until': date_until,
							'adults': adults,
							'ninos': childrens,
							'rooms': num_rooms,
							'include_room': include_room,
							'include_food': true,
							"lunch": lunch_dict,
							"dinner": dinner_dict,
							"include_transport": add_transport,
							"origen": origen,
							"destiny": destiny,
							'showContainerRoom': document.getElementById('room_check').checked,
							'showContainerFood': document.getElementById('food_check').checked,
						},
					}).then(result => {
						self.unblockUI(ev);
						if (result.error_validation) {
							self.MessageDialog(result.title_error, result.content_error)
							return
						};
						if (result.reserved){
							window.location = '/reserved/' + `${result.reservation_id}`+ '?reserve=True'+'&token='+`${result.token}`
						}
					});
				}

			}
			else {
				this._rpc({
					route: '/reservation/search_reservation',
					params: {
						'children_list': children_objects,
						'has_partner': has_partner,
						'rooms': num_rooms,
						'names': list_of_names,
						'vats': list_of_cis,
						'emails': list_of_emails,
						'phones': list_of_phones,
						'institution_name': institution.value,
						'date_from': date_from,
						'date_until': date_until,
						'adults': adults,
						'ninos': childrens,
						'rooms': num_rooms,
						'include_room': include_room,
						'include_food': false,
						"include_transport": add_transport,
						"origen": origen,
						"destiny": destiny,
						'showContainerRoom': document.getElementById('room_check').checked,
						'showContainerFood': document.getElementById('food_check').checked,
					},
				}).then(result => {
					if (result.error_validation) {
						self.MessageDialog(result.title_error, result.content_error)
						return
					};
					if (result.reserved){
						window.location = '/reserved/' + `${result.reservation_id}`+ '?reserve=True'+'&token='+`${result.token}`
					}
				});

			}

			} else {
				// Cancelar la acción si el usuario hace clic en "Cancelar" o cierra el cuadro de diálogo
				alert("La acción ha sido cancelada. Puede presionar el botón de nuevo cuando esté seguro.");
				return
			}
				
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
			let first_last_name_input = document.getElementById("first_last_name_input")
			let phone_input = document.getElementById("phone_input")
			let email_input = document.getElementById("email_input")
			let institution = document.getElementById("institution")

			if (first_last_name_input.value == "" || phone_input.value == "" || email_input.value == "" || institution.value == "") {
				alert("Por favor Introduzca todos los datos necesarios de la persona que nos visita")
				return
			}
			
			var checkbox = $('[name="reserva"]:checked').map(function(){
				return this.value;
			  }).get();
			console.log(checkbox)

			// var containers = $('.selectDay').map(function(){
			// 	return this;
			// }).get();
			var date_from = $('#dateFrom').val();
			var date_until = $('#date_until').val();
			// var adults = $('#evaluar_adults').val();
			// var ninos = $('#evaluar_ninos').val();
			// var rooms = $('#evaluar_rooms').val()
			// var $showContainerRoom = $('#showContainerRoom').prop("checked")
			// var $showContainerFood = $('#showContainerFood').prop("checked")
			// var self = this;
			// // var fecha =  new Date();
			// // var fecha_datefrom =  new Date(date_from);
			// // var dia_datefrom = fecha_datefrom.getDate() + 1;
			// // var today = fecha.getDate();
			// var foodList = [];
			// $.each(containers, function(index, container) {
			// 	var $container = $(container);
			// 	var $breakfastLabel = $container.find('.evaluar_breakfast');
			// 	var $dinnerLabel = $container.find('.evaluar_dinner');
			// 	var $lunchLabel = $container.find('.evaluar_lunch');
			// 	var date = $container.data('date')
			// 	var breakfastValue = Number(parseInt($breakfastLabel.text()));
			// 	var dinnerValue = Number(parseInt($dinnerLabel.text()));
			// 	var lunchValue = Number(parseInt($lunchLabel.text()));
			// 	var data = {
			// 		date: date,
			// 		order: [
			// 			{
			// 			quantity: breakfastValue,'code':'DESAYUNO'
			// 		},
			// 			{
			// 			quantity: lunchValue,'code':'ALMUERZO'
			// 		},
			// 			{
			// 			quantity: dinnerValue,'code':'CENA'
			// 		}
			// 	]
					
			// 	};
			
			// 	foodList.push(data);
				
			// });
			this._rpc({
				route: '/reservation/reserved_rooms',
				params: {
					'ids': checkbox,
					'date_from': date_from,
					'date_until': date_until,
					// 'adults': adults,
					// 'ninos': ninos,
					// 'rooms': rooms,
					// 'foodList': foodList,
					// 'reserve_food': $showContainerFood,
					// 'reserve_room': $showContainerRoom,
				},
			}).then(data => {
				console.log(data)
				// if (dia_datefrom === today || Number(adults) === 0) {
				if (data.error_validation) {
					self.showerror(data.error_validation);
				}else{
					// window.location = '/reserved/' + `${data.reservation_id}`+ '?reserve=True'+'&token='+`${data.token}`
					console.log("ok")
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
