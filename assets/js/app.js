// d = new Dialog("Hello World", "Quote not loaded, click Show Quote button to motivate you.", {
//     "backdrop": "static"
// });

// d.setButtons([
//     {
//         name: "Show Quote",
//         class: "btn-primary",
//         onClick: function(event){
//             console.log(event);
//             var settings = {
//                 "url": "https://type.fit/api/quotes",
//                 "method": "GET",
//                 "timeout": 0,
//               };
              
//             $.ajax(settings).done(function (response) {
//                 console.log(response);
//                 var items = JSON.parse(response);
//                 var quote = items[Math.floor(Math.random()*items.length)];
//                 var template = `<figure>
//                     <blockquote class="blockquote text-center">
//                     <p class="ps-2">${quote.text}</p>
//                     </blockquote>
//                     <figcaption class="blockquote-footer text-center">
//                     <cite title="Source Title">${quote.author}</cite>
//                     </figcaption>
//                 </figure>`;
//                 $(event.data.modal).find(".modal-body").html(template);
//             });
//         }
//     },
//     {
//         name: "Close",
//         class: "btn-warning",
//         // dismiss: true,
//         onClick: function(event){
//             $(event.data.modal).modal('hide');
//         }
//     }
// ]);

// d.show();

const animateCSS = (element, animation, prefix = 'animate__') =>
    // We create a Promise and return it
    new Promise((resolve, reject) => {
      const animationName = `${prefix}${animation}`;
      const node = document.querySelector(element);
  
      node.classList.add(`${prefix}animated`, animationName);
  
      // When the animation ends, we clean the classes and resolve the Promise
      function handleAnimationEnd(event) {
        event.stopPropagation();
        node.classList.remove(`${prefix}animated`, animationName);
        resolve('Animation ended');
      }
  
      node.addEventListener('animationend', handleAnimationEnd, {once: true});
    });
  
  $('.btn-add-api-key').on('click', function(){
      $.get('/api/dialogs/api_keys', function(data, status, xhr){
          d = new Dialog("Add API Key", data);
          d.setButtons([
              {
                  "name": "Generate Key",
                  "class": "btn-success btn-generate-key",
                  "onClick": function(event){
                      var modal = $(event.data.modal);
                      var name = modal.find('#api-name').val(); //gets necessary input from modal using id
                      var group = modal.find('#api-group').val();
                      var remarks = modal.find('#api-remarks').val();
  
                      if(name.length <=3 || group.length <= 3){ //checks name and group input length
                          // alert("API name and group cannot be empty");
                          animateCSS('.btn-generate-key', 'headShake')
                          return;
                      } else {
                          $.post('/api/v1/create/key', { // If ok, sends post request to /api/v1/create/key endpoint
                              'name': name,
                              'group': group,
                              'remarks': remarks
                          }, function(data, status, xhr){
                              if(status == 'success'){
                                  var modal = $(event.data.modal);
                                  $(modal).modal('hide'); // If post req success, closes the modal and displays the api key
                                  key = new Dialog("API Key", data.key);
                                  key.show();
                                  $.get('/api_keys/row?hash='+data.hash, function(data, status, xhr){
                                    if(status=="success"){
                                        $("#api_key_table").append(data);
                                        //TODO: Check if we need to reinitialize click event for delete button, since its dynamically added to DOM.
                                    }
                                });
                              } else {
                                  alert(data.message); 
                              }
                          });
                      }
                  }
              },
              {
                  "name": "Dismiss",
                  "class": "btn-secondary",
                  "dismiss": true
              }
          ])
          d.show();
      });
  });
  
  $('.btn-api-enable').on('click', function(){
    var id = $(this).attr('id');
    var status = $(this).is(':checked');
    var row = $(this).parent().parent().parent();
    console.log(row);
    $.post('/api_keys/enable', {
        'id': id,
        'status': status
    }, function(data, status, xhr){
        if(data.status){
            $(row).find('.api-status-badge').removeClass('bg-gradient-secondary').addClass('bg-gradient-success').html('ACTIVE');
        } else {
            $(row).find('.api-status-badge').removeClass('bg-gradient-success').addClass('bg-gradient-secondary').html('INACTIVE');
        }
    });
});

    $('.btn-delete-api-key').on('click', function(){
        var rowid = $(this).attr('data-rowid');
        $.get('/api_keys/row/delete_dialog?hash='+rowid, function(data, status, xhr){
            d = new Dialog("Delete API Key", data);
            d.setButtons([
                {
                    "name": "Delete",
                    "class": "btn-danger btn-delete-key",
                    "onClick": function(event){
                        $.get('/api_keys/row/delete?hash='+rowid, function(data, status, xhr){
                            if(status == 'success'){
                                var modal = $(event.data.modal);
                                $(modal).modal('hide');
                                $('#row-'+rowid).remove();
                            }
                        })
                    }
                },
                {
                    "name": "Cancel",
                    "class": "btn-secondary",
                    "dismiss": true
                }
            ])
            d.show();
        })
    });


  $('.btn-add-api-group').on('click', function(){ //for group, we put the necessary html here itself instead of seperate file like api_keys.html for api keys
      d = new Dialog("Add Group", `
      <form>
          <div class="form-group">
              <label for="group-name">Group Name</label>
              <input type="text" class="form-control" id="group-name" placeholder="Cameras">
          </div>
          <div class="form-group">
              <label for="group-desc">Description</label>
              <textarea class="form-control" id="group-desc" rows="2"></textarea>
          </div>
      </form>
      `);
      d.setButtons([
          {
              "name": "Add Group",
              "class": "btn-success btn-add-group",
              "onClick": function(event){
                  var modal = $(event.data.modal);
                  console.log(modal);
                  var groupName = modal.find('#group-name').val(); //get necessary inputs from modals
                  var groupDesc = modal.find('#group-desc').val();
                  if(groupName.length <=3 || groupDesc.length <= 5){ //length check
                      // alert("Group name cannot be empty");
                      animateCSS('.btn-add-group', 'headShake')
                      return;
                  } else {
                      $.post('/api/v1/create/group', {  // If ok, send post req to /api/v1/create/group endpoint
                          'name': groupName, 
                          'description': groupDesc
                      }, function(data, status, xhr){
                          if(data.status == 'success'){
                              var modal = $(event.data.modal);
                              $(modal).modal('hide'); // If post req is success, close the modal
                          } else {
                              // alert(data.message);
                          }
                      });
                  }
              }
          },
          {
              "name": "Cancel",
              "class": "btn-secondary",
              "onClick": function(event){
                  var modal = $(event.data.modal);
                  $(modal).modal('hide');
              }
          }
      ]);
      d.show();
  
  });
  