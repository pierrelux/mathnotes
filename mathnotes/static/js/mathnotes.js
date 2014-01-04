$("#menu-close").click(function(e) {
    e.preventDefault();
    $("#sidebar-wrapper").toggleClass("active");
});
$("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#sidebar-wrapper").toggleClass("active");
});

var Reference = $$({
  model: {},
  view: { format: '<li class="list-group-item">\
                   <button type="button" class="close pull-right" aria-hidden="true">&times;</button>\
                   <h4 class="list-group-item-heading"><span data-bind="title"/></h4>\
                   <span data-bind="authors"/></li>'
  },
  controller: {
   'click button': function(){
      this.destroy();
    }
  }
});

var ReferenceList = $$({
    model: {},
    view: { format: '<ul class="list-group"></ul>' },
    controller: {}
});

var NoteEditor = $$({
  model: {title:'Title', text:'Write your note'},
  view: { format: $('#noteEditor').html().trim() },
  controller: {
  'submit &': function(e){
        e.preventDefault();
        console.log('Saving');
        this.save();
   },
  'persist:save:success': function(){
       console.log('Saved');
   }
  }
});

NoteEditor.persist($$.adapter.restful, {collection:'notes', baseUrl:'/'});

$$.document.append(NoteEditor, $('#noteEditor'))
$('#referenceSearch').typeahead({
    name: 'accounts',
    prefetch: {
    url: '/references/hints/typeahead',
    filter: function(resp) { return resp.items; }
    },
    remote: {
    url: '/references/typeahead/%QUERY',
    filter: function(resp) { return resp.items; }
    },
    template: [
    '<p class="tt-suggestion-year">{{date}}</p>',
    '<p class="tt-suggestion-title">{{value}}</p>',
    '<p class="tt-suggestion-authors">{{authors}}</p>'
    ].join(''),
    engine: Hogan
});

$$.document.append(NoteEditor, $('#content'));
$$.document.after(ReferenceList, $('#textEditor'));
$('#referenceSearch').on('typeahead:selected', function (object, datum) {
    var ref = $$(Reference, {title: datum['title'], authors: datum['authors']});
    ReferenceList.append(ref);
    $('#referenceSearch').val('');
});
    var ref = $$(Reference, {title: 'Some Title', authors: 'Authors'})
    ReferenceList.append(ref);
