define([], function() {
    window.modul['__default_panel__'] = {
        history_click: function(ev) {
            let data = ev.data
            var h_cards = $('#content_modul_page_'+data.modul).find('.sh_card')
            if (h_cards.length > data.card) {
              var h_card =  $(h_cards[data.card])
              var h_card_entries = h_card.children()
              if (h_card_entries.length > data.entry) {
                var entry = $(h_card_entries[data.entry])
                var label = entry.data('entry')
                var sensor = h_card.data('sources')[label]
                if (sensor != undefined) {
                  window.api_call(url='sm/history_chart', data={'panel': data.modul, 'sensor': sensor}).then(resp => {
                    if (resp.ok) {
                      require(['lcwindowchart'], function(lcWindowChart) {
                        if ($('#chartwin').length == 0) {
                          $('body').append('<div id="chartwin" />')
                          $('#chartwin').lcWindowChart()
                        }
                        $('#chartwin').lcWindowChart('show', resp.data)
                      })
                    }
                  })
                }
              }
            }
        },
        history_create: function(panel, card_id) {
          var h_cards = $('#content_modul_page_'+panel).find('.sh_card')
          console.log(panel)
          if (h_cards.length > card_id) {
            var h_card_entries = $(h_cards[card_id]).children()
            for (var h1=0; h1<h_card_entries.length; h1++) {
              var entry = $(h_card_entries[h1])
              if (entry.hasClass('sh_card_history')) {
                entry.css('cursor', 'pointer')
                var span = $(entry.find('.sh_card_item_labels')[0])
                span.after('<img class="sh_card_item_img" src="/img/mdi/chart-bell-curve-cumulative.svg" ' +
                           'height="16px" width="16px" style="left: 16px" onload="SVGInject(this)">')
                entry.off('click')
                entry.on('click', null, {modul: panel, card: card_id, entry: h1},  window.modul[panel].history_click)
              }  
            }
          }
        }    
    }
})

