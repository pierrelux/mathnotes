$("#menu-close").click(function(e) {
    e.preventDefault();
    $("#sidebar-wrapper").toggleClass("active");
});
$("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#sidebar-wrapper").toggleClass("active");
});

var Reference = $$({},
  '<li><span data-bind="content"></span></li>',
   {});

var ReferenceList = $$({},
      '<div><h4>References</h4>\
         <ul></ul>\
         <input id="reference-search" type="text" class="typeahead borderless form-control" data-bind="content" placeholder="Search by title or author">\
       </div>',
  {
  'keyup #reference-search': function(e){
     var code = e.keyCode || e.which;
     if (code == 13){
       var bibRef = $$(Reference, {content: this.model.get('content')});
       this.append(bibRef, "ul");
     }
   }
  });

var Note = $$({},
       '<div class="panel panel-default">\
       <div class="panel-heading"><input type="text" class="form-control" name="title" placeholder="Title"></div>\
       <div class="panel-body"><textarea name="text" class="form-control" rows="5">Write your stroke of thought</textarea>\
       <span id="references"/></div>\
	   <div class="panel-footer"><div class="btn-toolbar" role="toolbar">\
         <div class="btn-group">\
           <button type="button" class="btn btn-default"> <span class="glyphicon glyphicon-tags"></span></button>\
           <button type="button" id="referenceBtn" class="btn btn-default">\
             <span class="glyphicon glyphicon-link"></span>\
           </button>\
         </div>\
         <div class="btn-group pull-right">\
           <button type="submit" class="btn btn-primary">OK</button>\
         </div>\
       </div>\
      </div></div>',
   {
     'click #referenceBtn': function() {
        var refList = $$(ReferenceList, {});
        this.append(refList, $('#references'));
        $('#reference-search').typeahead({
          name: 'accounts',
          prefetch: '/references',
          remote: '/references/search/%QUERY',
          template: [
           '<p class="tt-suggestion-year">{{year}}</p>',
           '<p class="tt-suggestion-title">{{value}}</p>',
           '<p class="tt-suggestion-authors">{{authors}}</p>'
          ].join(''),
          engine: Hogan
        });
        // todo prefetch tems?format=atom&content=json&order=dateAdded from backend. Parse + return to datum format
        $('#reference-search').on('typeahead:selected', function (object, datum) {
           var bibRef = $$(Reference, {content: datum['value']});
           refList.append(bibRef, "ul");
         });
      }
   }
);

$$.document.append(Note, $('#noteEditor'))
