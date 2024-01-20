///////// CONFIG LOGIN
var username = document.getElementById('username').value;
var password = document.getElementById('password').value;

var formData = new FormData();
formData.append('username', username);
formData.append('password', password);


////////////////////////////// LOGIN /////////////////////////////////////


(function ($) {
  "use strict";

  /*==================================================================
  [ Validate ]*/
  var input = $('.validate-input .input100');

  $('.validate-form').on('submit',function(){
      var check = true;

      for(var i=0; i<input.length; i++) {
          if(validate(input[i]) == false){
              showValidate(input[i]);
              check=false;
          }
      }

      return check;
  });


  $('.validate-form .input100').each(function(){
      $(this).focus(function(){
         hideValidate(this);
      });
  });

  function validate (input) {
      if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
          if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
              return false;
          }
      }
      else {
          if($(input).val().trim() == ''){
              return false;
          }
      }
  }

  function showValidate(input) {
      var thisAlert = $(input).parent();

      $(thisAlert).addClass('alert-validate');
  }

  function hideValidate(input) {
      var thisAlert = $(input).parent();

      $(thisAlert).removeClass('alert-validate');
  }
  
  /*==================================================================
  [ Show pass ]*/
  var showPass = 0;
  $('.btn-show-pass').on('click', function(){
      if(showPass == 0) {
          $(this).next('input').attr('type','text');
          $(this).find('i').removeClass('fa-eye');
          $(this).find('i').addClass('fa-eye-slash');
          showPass = 1;
      }
      else {
          $(this).next('input').attr('type','password');
          $(this).find('i').removeClass('fa-eye-slash');
          $(this).find('i').addClass('fa-eye');
          showPass = 0;
      }
      
  });
  

})(jQuery);


// $(document).ready(function () {
//   $('.validate-form').submit(function (event) {
//     event.preventDefault();

//     var username = $('#username').val();
//     var password = $('#password').val();

//     var formData = new FormData();
//     formData.append('username', username);
//     formData.append('password', password);

//     // Send the login request to the server
//     $.ajax({
//       url: '/',
//       type: 'POST',
//       data: formData,
//       processData: false,
//       contentType: false,
//       success: function (response) {
//         // Check if the response contains the "error_message" variable
//         if (response.includes("error_message")) {
//           // Show the error message on the page
//           $('.alert-danger').text(response.error_message).show();
//         } else {
//           // Redirect to the home page
//           window.location.href = '/home';
//         }
//       },
//       error: function (xhr, status, error) {
//         // Show the error message on the page
//         $('.alert-danger').text('An error occurred').show();
//       }
//     });
//   });

//   $('.validate-form .input100').each(function () {
//     $(this).focus(function () {
//       hideAlert($(this));
//     });
//   });

//   function hideAlert(input) {
//     var thisAlert = $(input).parent();
//     $(thisAlert).removeClass('alert-validate');
//   }
// });


////////////////////////////// REGISTER /////////////////////////////////////


// $(document).ready(function () {
//     $('form').submit(function (event) {
//         event.preventDefault();

//         var password = $('#register-password').val();
//         var confirmPassword = $('#register-confirm-password').val();

//         if (password !== confirmPassword) {
//             // Passwords don't match, show Bootstrap alert
//             $('#passwordMismatchAlert').show();
//         } else {
//             // Passwords match, hide the alert and continue with form submission
//             $('#passwordMismatchAlert').hide();
//             this.submit();
//         }
//     });
// });