odoo.define('login_id.signup', function (require) {
'use strict';
var rpc = require('web.rpc');
var ajax = require('web.ajax');
var publicWidget = require('web.public.widget');


var SignUpFormExtension = publicWidget.registry.SignUpForm.extend({
    events: {
        'click .sent_otp': '_onClick',
        'click button[type="submit"]': '_onSubmitClick',
    },

    async willStart() {
        var button = this.$('.btn-primary').attr('disabled','disabled');
        this.$("#div-timer").css("display","none");
        let timer = window.localStorage.getItem("timer")
        let updatedTimestamp = window.localStorage.getItem("updatedTimestamp")
        if (timer > 0) {
            this.idle_timer(timer, updatedTimestamp)
            this.$('#div-timer').css("display", "block");
            this.$('.sent_otp').attr('disabled','disabled');
            var button = this.$('.btn-primary').removeAttr('disabled');
        }

    },

    _onClick: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        const Mobile = $("#user_login_mob")[0].value
        const CountryCode = $(".div_code")[0].value
        var val = /^\d{8}$/.test(Mobile);
        if(!val){
            ev.preventDefault();
            alert('Please add Valid Mobile number ');
        }
        else{
            this.idle_timer(0, 0)
            this.$('.sent_otp').attr('disabled','disabled');
            var button = this.$('.btn-primary').removeAttr('disabled');
            this.$('.sent_otp').css("background","#5097A4");
            this.$('.sent_otp').css("border-radius", "25px");
            this.$('#div-timer').css("display", "block");
            var digits = '0123456789';
            let OTP = '';
            for (let i = 0; i < 4; i++ ) {
                OTP += digits[Math.floor(Math.random() * 10)];
            }
            window.localStorage.setItem("OTP", OTP)
            console.log('otp', OTP)
            ajax.rpc('/web/send_sms', {
            'country_code' : CountryCode,
            'phone': Mobile,
            'otp': OTP,
            })
        }
    },

    idle_timer: function(timer, Timestamp) {
        var self = this
        var nowt = new Date().getTime();
        var date = new Date(nowt);
        var time = date.setMinutes(date.getMinutes() + 5);
        var updatedTimestamp = date.getTime();
        if (timer > 0){
            var updatedTimestamp = Timestamp
        }
        /** Running the count down using setInterval function */
        var idle = setInterval(function() {
            var now = new Date().getTime();
            var distance = updatedTimestamp - now;
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            self.el.querySelector("#idle_timer").innerHTML = minutes + "m " + seconds + "s ";
            window.localStorage.setItem("timer", distance)
            window.localStorage.setItem("updatedTimestamp", updatedTimestamp)

            /** if the countdown is zero the link is redirect to the login page*/
            if (distance < 0) {
                clearInterval(idle);
                self.el.querySelector("#idle_timer").innerHTML = "EXPIRED";
                this.$('.sent_otp').removeAttr('disabled');
                var button = this.$('.btn-primary').attr('disabled','disabled');
            }
        }, 1000);
    },
    _onSubmitClick: function (ev) {
        let OTP = window.localStorage.getItem("OTP")
        let otp_val = $("#sms_number")[0].value
        if (OTP != otp_val){
            ev.preventDefault();
            alert('OTP is not Matching');
        }
        else{
            this.$('.sent_otp').removeAttr('disabled');
            var button = this.$('.btn-primary').attr('disabled','disabled');
        }

    },

});
    publicWidget.registry.SignUpForm = SignUpFormExtension;
});