odoo.define('hotel_reservation.HomeReservations', function (require) {

	"use strict";


  var publicWidgetHome = require('web.public.widget');

  publicWidgetHome.registry.HomeReservations = publicWidgetHome.Widget.extend({
    
    selector: '#body',
    xmlDependencies: ['/hotel_reservation/static/src/xml/home_reservation.xml',],

    start: function () {
      const initBg = (autoplay = true) => {
        const bgImgsNames = ['san_juan1.jpeg', 'san_juan2.jpg', 'san_juan3.jpeg'];
        const bgImgs = bgImgsNames.map(img => "/hotel_reservation/static/src/img/" + img);
  
        $.backstretch(bgImgs, {duration: 4000, fade: 500});
  
        if(!autoplay) {
          $.backstretch('pause');
        }
    }
  
    const setBg = id => {
        $.backstretch('show', id);
    }
  
    const setBgOverlay = () => {
        const windowWidth = window.innerWidth;
        const bgHeight = $('.body').height();
        const tmBgLeft = $('.tm-bg-left');
  
        $('.tm-bg').height(bgHeight);
  
        if(windowWidth > 768) {
            tmBgLeft.css('border-left', `0`)
                    .css('border-top', `${bgHeight}px solid transparent`);
        } else {
            tmBgLeft.css('border-left', `${windowWidth}px solid transparent`)
                    .css('border-top', `0`);
        }
    }
  
    $(document).ready(function () {
        const autoplayBg = true;	// set Auto Play for Background Images
        initBg(autoplayBg);
        setBgOverlay();
  
        const bgControl = $('.tm-bg-control');
        bgControl.click(function() {
            bgControl.removeClass('active');
            $(this).addClass('active');
            const id = $(this).data('id');
            setBg(id);
        });
  
        $(window).on("backstretch.after", function (e, instance, index) {
            const bgControl = $('.tm-bg-control');
            bgControl.removeClass('active');
            const current = $(".tm-bg-controls-wrapper").find(`[data-id=${index}]`);
            current.addClass('active');
        });
  
        $(window).resize(function() {
            setBgOverlay();
        });
    });
  },

  });
});