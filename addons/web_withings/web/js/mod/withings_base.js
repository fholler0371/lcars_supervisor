define([], function() {
    window.modul['withings_base'] = {
        modul: true,
        icon: '/img/mdi/human-handsdown.svg',
        label: 'Basisdaten',
        already_init : false,
        init: function () {
        },
        set_content: function() {
            let self = window.modul['withings_base']
            if (!($('#content_modul_withings_base').length)) {
                let html = '<div id="content_withings_base_panel" class="content_modul"></div>'
                $(".main_content").append(html)
                require([], function() {
                    window.api_call(url='sm/get_cards', data={'panel': 'base'}).then(resp => {
                        if (resp.ok) {
                            let _cards = resp.data.cards
                            let req = ['packery', 'lcsmcard']
                            for (var i=0; i<_cards.length; i++) {
                                let req_entry = {}
                                if (_cards[i].type == 'app') {
                                    req_entry['card_'+_cards[i].name] = '/withings/js/mod/cards/'+ _cards[i].name
                                }
                                require.config({paths: req_entry})
                                req.push('card_'+_cards[i].name)
                            }
                            let items = resp.data.items
                            console.log(req)
                            require(req, function(Packery){
                                console.log(req)
                                for (var j=0; j<items.length; j++) {
                                    let type = items[j].type
                                    let item_data = [items[j].type]
                                    if (items[j].data != undefined) {
                                        for (k=0; k<items[j].data.length; k++) {
                                            item_data.push(items[j].data[k])
                                        }
                                    }
                                    cards[type].create('withings_panel', items[j]['label'], j, item_data)
                                    console.log(items[j])
                                }
                            })
                            console.log(resp)
                        }
                    })
                })
            } 
            $('#content_modul_withings_base').show()
        },
        show: function () {
            let self = window.modul['withings_base']
            window.modul['helper'].activate('withings_base', self.label)
            self.set_content()
        },
        stop: function() {
        
        }
    }
    window.modul['withings_base'].init()
});

// {
//     "cards": [
//       "withings_body",
//       "withings_weight_trend",
//       "withings_heart",
//       "withings_temp"
//     ],
//     "items": [
//       {
//         "label": "Körper",
//         "type": "withings_body",
//         "ver": 1
//       },
//       {
//         "label": "Gewichtsentwicklung",
//         "type": "withings_weight_trend",
//         "ver": 1
//       },
//       {
//         "label": "Herz",
//         "type": "withings_heart",
//         "ver": 1
//       },
//       {
//         "label": "Temperatur",
//         "type": "withings_temp",
//         "ver": 1
//       }
//     ]
//   }

/* define(function () {
  var _modul = {
    icon: '/js/img/mdi/human-handsdown.svg',
    already_init : false,
    label: 'Übersicht',
    init: function() {
      if (!window.modul['page_withings_panel'].already_init) {
        window.modul['page_withings_panel'].already_init = true
      }
    },
    update_data : function() {
      if ($('#content_modul_page_withings_panel').is(":visible")) {
        setTimeout(window.modul['page_withings_panel'].update_data, 15000)
        var sub_data = [],
            cards = $('#content_modul_page_withings_panel').children()
        for (var i=0; i<cards.length; i++) {
          if ($(cards[i]).data('sources') != null) { 
            sub_data.push($(cards[i]).data('sources'))
          }
        }
        postData('/api', { 'action': 'sensor_get', 'panel': 'withings_panel', 'sensors': sub_data }, token=true).then(data => {
          if (data.error != null) {
            console.error(data)
          } else {
            var cards = $('#content_modul_page_withings_panel').children()
            for (var i=0; i<data.length; i++) {
              if ($(cards[i]).hasClass('lcSmCard')) {
                $(cards[i]).lcSmCard('update', data[i])
              } else {
                var update = window.cards[$(cards[i]).data('type')].update
                update('withings_panel', i, data[i])
              }
            }
          }
        })
      }
    },
    show: function() {
      $('#header_appname').text(window.modul['page_withings_panel'].label)
      require(['jqxtabs', 'inject'], function() {
        if (!($('#content_modul_page_withings_panel').length)) {
          var html = '<div id="content_modul_page_withings_panel" class="content_modul">'
          html += '</div>'
          $(".main_content").append(html)
          postData('/api', { 'action': 'cards_get', 'panel': 'withings_panel' }, token=true).then(data => {
            if (data.error != null) {
              console.error(data)
            } else {
              var req = ['packery', 'lcsmcard']
              for (var i=0; i<data.cards.length; i++) {
                var card_entry = {}
                card_entry['card_'+data.cards[i].split('|')[0]] = ["/withings/js/cards/"+data.cards[i].split('|')[0], "/withings/js/cards/default"]
                require.config({paths: card_entry})
                req.push('card_'+data.cards[i].split('|')[0])
              }
              var card_data = data.items
              require(req, function(Packery){
                for (var j=0; j<card_data.length; j++) {
                  if (card_data[j].ver == 1) {
                    try {
                      cards[card_data[j]['type'].split('|')[0]].create('withings_panel', card_data[j]['label'], j, card_data[j]['type'].split('|'))
                    } catch(err) {
                      console.error(err)
                    }
                  } else if (card_data[j].ver == 2) {
                    let type = card_data[j].type
                    // load defition is needed
                    if ($.lcSmCard.defaults.types[type] == undefined) {
                      let data= postDataSync('/api', { 'action': 'cards_construct', 'type': type }, token=true)
                      if (data != undefined) {
                        $.lcSmCard.defaults.types[type] = data
                      }
                    }
                    let div = '<div id="smcard_'+'withings_panel'+'_'+j+'"></div>'
                    $('#content_modul_page_withings_panel').append(div)
                    $('#smcard_'+'withings_panel'+'_'+j).lcSmCard({type: card_data[j].type, ver: card_data[j].ver, panel: 'withings_panel', label: card_data[j].label, id: j})
                  } 
                }
                $('#content_modul_page_withings_panel').data('packery', new Packery( '#content_modul_page_withings_panel', {itemSelector: '.sh_card', gutter: 20}))
              })
            }
          })  
        }
        $('#content_modul_page_withings_panel').show()
        var packery = $('#content_modul_page_withings_panel').data('packery')
        if (!(packery == undefined)) {
          $('#content_modul_page_withings_panel').data('packery').layout()
        }
      })
      setTimeout(this.update_data, 1000)
    },
    hitory_create: function(card_id) {
      var h_cards = $('#content_modul_page_withings_panel').find('.sh_card')
      if (h_cards.length > card_id) {
        var h_card_entries = $(h_cards[card_id]).children()
        for (var h1=0; h1<h_card_entries.length; h1++) {
          var entry = $(h_card_entries[h1])
          if (entry.hasClass('sh_card_history')) {
            entry.css('cursor', 'pointer')
            var span = $(entry.find('.sh_card_item_labels')[0])
            span.after('<img class="sh_card_item_img" src="/js/img/mdi/chart-bell-curve-cumulative.svg" ' +
                       'height="16px" width="16px" style="left: 16px" onload="SVGInject(this)">')
            entry.off('click')
            entry.on('click', null, {modul: 'withings_panel', card: card_id, entry: h1},  window.modul['page_withings_panel'].history_click)
          }  
        }
      }
    },
    edit_create: function(card_id) {
      var h_cards = $('#content_modul_page_withings_panel').find('.sh_card')
      if (h_cards.length > card_id) {
        var h_card_entries = $(h_cards[card_id]).children()
        for (var h1=0; h1<h_card_entries.length; h1++) {
          var entry = $(h_card_entries[h1])
          if (entry.hasClass('sh_card_edit')) {
            entry.css('cursor', 'pointer')
            var span = $(entry.find('.sh_card_item_labels')[0])
            span.after('<img class="sh_card_item_img" src="/js/img/mdi/pencil.svg" ' +
                       'height="16px" width="16px" style="left: 16px" onload="SVGInject(this)">')
            let editmode = entry.data('editmode')
            entry.off('click')
            if ('undefined' != entry.data('editmode')) {
              let rs_paths = {}
              let rs_modul = 'lccarsds_dlg_'+editmode
              rs_paths[rs_modul] = '/js/lc/cards_dialogs/'+editmode
              requirejs.config({'paths': rs_paths})
              requirejs([rs_modul], function(){})
              entry.on('click', null, {modul: 'withings_panel', card: card_id, entry: entry.data('entry'), mode: entry.data('editmode')},  
                                window.modul['page_withings_panel'].edit_click)
            }
          }  
        }
      }
    },
    edit_click: function(ev) {
      let rs_modul = 'lccarsds_dlg_'+ev.data.mode
      requirejs([rs_modul], function(func){
        func(ev)
      })
    },
    history_click: function(ev) {
      var data = ev.data
      var h_cards = $('#content_modul_page_'+data.modul).find('.sh_card')
      if (h_cards.length > data.card) {
        var h_card =  $(h_cards[data.card])
        var h_card_entries = h_card.children()
        if (h_card_entries.length > data.entry) {
          var entry = $(h_card_entries[data.entry])
          var label = entry.data('entry')
          var sensor = h_card.data('sources')[label]
          if (sensor != undefined) {
            postData('/api', { 'action': 'history_chart', 'panel': 'withings_panel', 'sensor': sensor }, token=true).then(data => {
              if (data.error != null) {
                console.error(data)
              } else {
                require(['lcwindowchart'], function(lcWindowChart) {
                  if ($('#chartwin').length == 0) {
                    $('body').append('<div id="chartwin" />')
                    $('#chartwin').lcWindowChart()
                  }
                  $('#chartwin').lcWindowChart('show', data)
                })
              }
            })
          }
        }
      }
    }
  }
  window.modul['page_withings_panel'] = _modul
  console.log("page_withings_panel")
  return _modul
}) */