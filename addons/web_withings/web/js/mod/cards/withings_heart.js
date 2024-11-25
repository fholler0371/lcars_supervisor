define(function () {
    var card = {
      create : function(panel, label, id, _) {
        var html = '<div class="sh_card" data-panel="'+panel+'" data-id="'+id+'" data-type="withings_heart"><div class="sh_card_label">'+label+'</div></div>'
        $('#content_modul_page_'+panel).append(html)
        window.api_call(url='sm/cards_source', data={'panel': panel, 'card': id,
            'items': ['puls', 'systole', 'diastole', 'puls_wellen_elasitzitaet', 'gefaess_alter']}).then(resp => {
            if (resp.ok) {
            let data = resp.data
            var height = 32
            var values = {}
            var sources = {}
            var ele = $('#content_modul_page_'+panel).children()[id]
            if (data.puls != null && data.puls.value != null) {
              height += 24
              var html = '<div data-entry="puls" class="sh_card_history">'
              html += '<span class="sh_card_item_labels"  style="left: 5px; position: relative">Puls</span>'
              html += '<div class="sh_card_item_value"><span></span></div></div>'
              $(ele).append(html)
              values['puls'] = data.puls.value
              sources['puls'] = data.puls.source
            }
            if (data.systole != null && data.systole.value != null) {
              height += 24
              var html = '<div data-entry="systole" class="sh_card_history">'
              html += '<span class="sh_card_item_labels" style="left: 5px; position: relative">Systole</span>'
              html += '<div class="sh_card_item_value"><span></span> mmHg</div></div>'
              $(ele).append(html)
              values['systole'] = data.systole.value
              sources['systole'] = data.systole.source
            }
            if (data.diastole != null && data.diastole.value != null) {
              height += 24
              var html = '<div data-entry="diastole">'
              html += '<span class="sh_card_item_labels" style="left: 5px; position: relative">Diastole</span>'
              html += '<div class="sh_card_item_value"><span></span> mmHg</div></div>'
              $(ele).append(html)
              values['diastole'] = data.diastole.value
              sources['diastole'] = data.diastole.source
            }
            if ((data.puls_wellen_elasitzitaet != null) && (data.puls_wellen_elasitzitaet.value != null)) {
              height += 24
              var html = '<div data-entry="puls_wellen_elasitzitaet"  class="sh_card_history">'
              html += '<span class="sh_card_item_labels" style="left: 5px; position: relative">Pulswellen</span>'
              html += '<div class="sh_card_item_value"><span></span> m/s</div></div>'
              $(ele).append(html)
              values['puls_wellen_elasitzitaet'] = data.puls_wellen_elasitzitaet.value
              sources['puls_wellen_elasitzitaet'] = data.puls_wellen_elasitzitaet.source
            }
            if ((data.gefaess_alter != null) && (data.gefaess_alter.value != null)) {
              height += 24
              var html = '<div data-entry="gefaess_alter"  class="sh_card_history">'
              html += '<span class="sh_card_item_labels" style="left: 5px; position: relative">Gefässalter</span>'
              html += '<div class="sh_card_item_value"><span></span> Jahre</div></div>'
              $(ele).append(html)
              values['gefaess_alter'] = data.gefaess_alter.value
              sources['gefaess_alter'] = data.gefaess_alter.source
            }
            $(ele).height(height)
            $(ele).data('sources', sources)
            cards.withings_heart.update(panel, id, values)
            var packery = $(ele).parent().data('packery')
            if (packery != undefined) {
              packery.layout()
            }
            window.modul[panel].history_create(panel, id)
          }
        })
      },
      update : function(panel, id, values) {
        var eles = $($('#content_modul_page_'+panel).children()[id]).children()
        $($('#content_modul_page_'+panel).children()[id]).find('.sh_card_item_highlight').removeClass('sh_card_item_highlight')
        for (var i=0; i<eles.length; i++) {
          var ele = eles[i]
          if (($(ele).data('entry') == 'puls') && (values['puls'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['puls'].toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'systole') && (values['systole'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['systole'].toLocaleString('de-DE', {maximumFractionDigits: 0})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'diastole') && (values['diastole'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['diastole'].toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'puls_wellen_elasitzitaet') && (values['puls_wellen_elasitzitaet'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['puls_wellen_elasitzitaet'].toLocaleString('de-DE', {minimumFractionDigits: 2, maximumFractionDigits: 2})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'gefaess_alter') && (values['gefaess_alter'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['gefaess_alter'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
        }
      }
    }
    if (window.cards == undefined) { window.cards = {}}
    window.cards['withings_heart'] = card
  })