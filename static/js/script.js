jQuery(document).ready(function($) {


	// $('#forgotPass').click(function() {
	// 	$('#modalSignUp').modal('hide');
	// });

	// if ($("#q").val().length > 0) $("#question-mask").hide(){
	// 	    $("#q").bind("autocompleteopen", function(event, ui) {
	// 	    $('.ui-autocomplete').css('width','230px');
	//   	});
	// }

	// if(google.loader.ClientLocation){
	//     $('#interaction_lat').val(google.loader.ClientLocation.latitude);
	//     $('#interaction_lng').val(google.loader.ClientLocation.longitude);
	//     $('#interaction_city').val(google.loader.ClientLocation.address.city);
	//     $('#interaction_region').val(google.loader.ClientLocation.address.region);
	//     $('#interaction_country').val(google.loader.ClientLocation.address.country);
	//     $('#interaction_country_code').val(google.loader.ClientLocation.address.country_code);
 //  	}
 //  	$('#email_body').textarea_maxlength();
	//     $('#new_email').validate({
	//        submitHandler: function(form) {
	//         $('#email_submit').attr('disabled',true);
	//         $('#email_submit').addClass('disabled');
	//         $('#email_submit_spinner').show();
	//          form.submit();
	//        },
	//        messages:{
	//          'interaction[name]':{
	//            'required':'Name is required.'
	//          },
	//          'interaction[email]':{
	//            'required':'Email address is required.',
	//            'email':'Invalid email address'
	//          },
	//          'email[subject]':{
	//            'required':'Subject is required.'
	//          },
	//          'email[body]':{
	//            'required':'Message is required.',
	//            'maxlength':'Exceeding max length of 5KB'
	//          }
	//        },
	//        rules:{
	//          'interaction[name]':{
	//            'required':true
	//          },
	//          'interaction[email]':{
	//            'required':true,
	//            'email':true
	//          },
	//          'email[subject]':{
	//            'required':true,
	//            'invalidchars':''
	//          },
	//          'email[body]':{
	//            'required':true,
	//            'maxlength':5000,
	//            'invalidchars':''
	//          }
	//        },
	//        errorClass:'invalid'
	// 	});
	

	// 	var autocomplete_source = '/customer/portal/articles/autocomplete'
 //           if ($('form').hasClass('support-search-small')) {
 //             autocomplete_source += '?size=small&';
 //           } else {
 //             autocomplete_source += '?';
 //           }
           
 //        $("#q").autocomplete({ 
 //             delay: 200,
 //             minLength: 2,
 //             search: function(event, ui) { $("#q").autocomplete("option", "source", autocomplete_source + 'rand=' + Math.round(Math.random() * 100000000000).toString()); },
 //             select: function(event, ui) { $(location).attr('href', ui.item.id); },
 //             focus: function(event, ui) { return false; }
 //        });
         
 //           $('#q').focus(function(){
 //             $('#question-mask').hide();
 //           });
           
 //           $('#q').blur(function(){
 //             if ($(this).val().length == 0) {
 //               $('#question-mask').show();
 //             }
 //           });
           
 //           $('#question-mask').click(function() {
 //             $('#q').focus();
 //           });
         
 //           $('form').submit(function(){
 //               $('input[type=text]').each(function(){
 //               $(this).val($.trim($(this).val()))
 //             });
 //           });
           
 //           // Extra validator added to handle invalid characters
 //           $.validator.addMethod('invalidchars', function(value, element, param) {
 //             return this.optional(element) || ! new RegExp('['+param+']').test(value);
 //           }, "Invalid characters found");
    

 //    $( "#q" ).bind("autocompleteopen", function(event, ui) {
	//    $('.ui-autocomplete').css({'margin':'0 0 0 -5px', 'width':'845px'});
	// });

	// if ($("#q").val().length > 0) $("#question-mask").hide(){

 //        $("#q").bind("autocompleteopen", function(event, ui) {
 //          	$('.ui-autocomplete').css('width','230px');
 //        });
 //    }

	// $.get('/customer/en/portal/articles/392582/is_rateable.json', function(json) {
 //        if (json.is_rateable) {
 //           $("#rate_article_container").show();
 //        }
 //    });



});