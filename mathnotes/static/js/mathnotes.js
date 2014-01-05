$("#menu-close").click(function(e) {
    e.preventDefault();
    $("#sidebar-wrapper").toggleClass("active");
});
$("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#sidebar-wrapper").toggleClass("active");
});

safe_restful = function(_params){
    var params = $.extend({
      dataType: 'json',
      url: (this._data.persist.baseUrl || 'api/') + this._data.persist.collection + (_params.id ? '/'+_params.id : ''),
      dataFilter: function(data, type) {
        data_parsed = JSON.parse(data);
        if ('items' in data_parsed) {
            data_parsed = data_parsed['items'];
        }
        return JSON.stringify(data_parsed)
      }
    }, _params);
    $.ajax(params);
  };

var Note = $$({
  model: {id:'', referenceIds:'', title:'', text:''},
  view: { format: $('#note').html().trim() },
  controller: {}
}).persist(safe_restful, {collection:'notes', baseUrl:'/'});

var NoteList = $$({}, '<span></span>').persist();

var Reference = $$({
  model: {title:'', authors:''},
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

var NoteEditor = $$({
  model: {title:'', text:'', referenceIds:''},
  view: { format: $('#NoteEditorTemplate').html().trim() },
  controller: {
  'submit &': function(e){
        e.preventDefault();
        if (this.model.get('title') || this.model.get('text') || this.model.get('referenceIds')) {
            console.log('Saving');
            this.save();
        }
   },
  'persist:save:success': function(){
       console.log('Saved');
       note = $$(Note, {title:this.model.get('title'), text:this.model.get('text')});
       NoteList.prepend(note);
       this.model.reset();
   },
   'typeahead:selected #referenceSearch': function(object, datum) {
        var ref = $$(Reference, {title: datum['title'], authors: datum['authors'], id: datum['source']});
        this.append(ref, $('#referenceList'));
        $('#referenceSearch').val('');
   },
   'append': function() {
        this.update_reflist();
    },
   'remove': function() {
        this.update_reflist();
    }
  },
  update_reflist: function() {
    // Agility.js doesn't seem to know how to marshall lists.
    // Manual housekeeping as a hack down here:
    ids = [];
    this.each(function (id, item) {
        ids.push(item.model.get('id'));
    });
    this.model.set({referenceIds: JSON.stringify(ids)});
    console.log(this.model.get('referenceIds'));
  }
}).persist(safe_restful, {collection:'notes', baseUrl:'/'});

$$.document.append(NoteEditor, $('#content'));
$$.document.append(NoteList, $('#content'));
NoteList.gather(Note, 'append');

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


