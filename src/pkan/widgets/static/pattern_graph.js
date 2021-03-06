// jshint ignore: start
/* More flexible Content loader pattern.
 *
 * Options:
 *    ajax_url(string): URL to load cytocape graph data from..
 *    trigger(string): Event to trigger content loading. Defaults to "immediate"
 *
 */

require([
  'jquery',
  'pat-base',
  'pat-logger',
  'pat-registry',
  'mockup-utils',
  'cytoscape',
  'cytoscape-cose-bilkent',
  'cytoscape-dagre',
  'underscore',
], function($, Base, logger, Registry, utils, cytoscape, coseBilkent, dagre, _) {
  'use strict';
  var log = logger.getLogger('pat-graph');
  console.log('pat-graph');

  var ContentLoader = Base.extend({
    name: 'graph',
    trigger: '.pat-graph',
    parser: 'mockup',
    defaults: {
      ajax_url: null,
      trigger: 'immediate',
      target: null,
      template: null,
      dataType: 'json',
      form_id: '',
      query_id: ''
    },
    init: function() {
      console.log('pat-graph: init');
      coseBilkent( cytoscape );
      dagre( cytoscape );
      var that = this;
      if(that.options.trigger === 'immediate'){
        that._load();
      }else{
        that.$el.on(that.options.trigger, function(e){
          e.preventDefault();
          that._load();
        });
      }
    },
    _cytoscape: function(data){
      var that = this;
      var cy = cytoscape({
        container: $('#cy'), // container to render in
        elements: data['elements'],
        style: cytoscape.stylesheet()
            .selector('node')
              .css({
                'font-size': 'data(pkfontsize)',
                'background-color': 'data(pkbackgroundcolor)',
                'shape': 'data(pkshape)',
                'width': 'data(pkwidth)',
                'content': 'data(title)',
                'text-halign': 'center',
                'text-valign': 'data(pkvalign)',
                'text-wrap': 'wrap',
                'text-max-width': '1000px',
                'height':'20',
                'border-color':'#000000',
                'border-width': 1,
                'border-color': 'data(pkbordercolor)',
                'opacity': 'data(pkopacity)'
              })
            .selector('edge')
              .css({
                'label': 'data(label)',
                'edge-text-rotation': 'autorotate'
              }),
//          layout: {
//            name: 'dagre',
//            }
        layout: {
        name: 'cose-bilkent',
        nodeRepulsion: 8000,
      }
        });
    },
    _load: function(){
      var that = this;
      that.$el.addClass('loading-content');
      if(that.options.ajax_url){
        that.loadRemote();
      }else{
        that.loadLocal();
      }
    },
    loadRemote: function(){
      var that = this;
      $.ajax({
        url: that.options.ajax_url,
        dataType: that.options.dataType,
        success: function(data){
          that._cytoscape(data);
        },
        error: function(){
          that.$el.addClass('content-load-error');
        }
      });
    },

  });

  return ContentLoader;

});
