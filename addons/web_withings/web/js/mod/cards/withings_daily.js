define(function () {
  var card = {
    create : function(panel, label, id, params) {
      var history = false
      if (params.length > 1 && params[1] == 'H') {
        history = true
      } 
      var html = '<div class="sh_card" data-panel="'+panel+'" data-id="'+id+'" data-type="withings_daily"><div class="sh_card_label">'+label+'</div></div>'
      $('#content_modul_page_'+panel).append(html)
      window.api_call(url='sm/cards_source', data={'panel': panel, 'card': id,
        'items': ['steps', 'distance', 'totalcalories', 'activecalories', 'activ_soft', 'activ_moderate', 'activ_intense']}).then(resp => {
        if (resp.ok) {
        let data = resp.data
          var height = 32
          var values = {}
          var sources = {}
          var ele = $('#content_modul_page_'+panel).children()[id]
          if (data.steps != null && data.steps.value != null) {
            height += 24
            var html = '<div data-entry="steps"'
            if (data.steps.params.includes('hist')) {
              html += ' class="sh_card_history"'
            }
            html += '><span class="sh_card_item_labels"  style="left: 5px; position: relative">Schritte</span>'
            html += '<div class="sh_card_item_value"><span></span></div></div>'
            $(ele).append(html)
            values['steps'] = data.steps.value
            sources['steps'] = data.steps.source
          }
          if (data.distance != null && data.distance.value != null) {
            height += 24
            var html = '<div data-entry="distance"'
            if (history) {
              html += ' class="sh_card_history"'
            }
            html += '><span class="sh_card_item_labels" style="left: 5px; position: relative">Strecke</span>'
            html += '<div class="sh_card_item_value"><span></span> km</div></div>'
            $(ele).append(html)
            values['distance'] = data.distance.value
            sources['distance'] = data.distance.source
          }
          if (data.totalcalories != null && data.totalcalories.value != null) {
            height += 24
            var html = '<div data-entry="totalcalories"'
            if (history) {
              html += ' class="sh_card_history"'
            }
            html += '><span class="sh_card_item_labels" style="left: 5px; position: relative">Kalorien (gesamt)</span>'
            html += '<div class="sh_card_item_value"><span></span> kcal</div></div>'
            $(ele).append(html)
            values['totalcalories'] = data.totalcalories.value
            sources['totalcalories'] = data.totalcalories.source
          }
          if ((data.activecalories != null) && (data.activecalories.value != null)) {
            height += 24
            var html = '<div data-entry="activecalories"'
            if (history) {
              html += ' class="sh_card_history"'
            }
            html += '><span class="sh_card_item_labels" style="left: 5px; position: relative">Kalorien (aktiv)</span>'
            html += '<div class="sh_card_item_value"><span></span> kcal</div></div>'
            $(ele).append(html)
            values['activecalories'] = data.activecalories.value
            sources['activecalories'] = data.activecalories.source
          }
          if ((data.activ_soft != null) && (data.activ_soft.value != null)) {
            height += 24
            var html = '<div data-entry="activ_soft"'
            if (history) {
              html += ' class="sh_card_history"'
            }
            html += '><span class="sh_card_item_labels" style="left: 5px; position: relative">Aktiv (leicht)</span>'
            html += '<div class="sh_card_item_value"><span></span> h</div></div>'
            $(ele).append(html)
            values['activ_soft'] = data.activ_soft.value
            sources['activ_soft'] = data.activ_soft.source
          }
          if ((data.activ_moderate != null) && (data.activ_moderate.value != null)) {
            height += 24
            var html = '<div data-entry="activ_moderate"'
            html += '><span class="sh_card_item_labels" style="left: 5px; position: relative">Aktiv (mittlere)</span>'
            html += '<div class="sh_card_item_value"><span></span> h</div></div>'
            $(ele).append(html)
            values['activ_moderate'] = data.activ_moderate.value
            sources['activ_moderate'] = data.activ_moderate.source
          }
          if ((data.activ_intense != null) && (data.activ_intense.value != null)) {
            height += 24
            var html = '<div data-entry="activ_intense"'
            html += '><span class="sh_card_item_labels" style="left: 5px; position: relative">Aktiv (hoch)</span>'
            html += '<div class="sh_card_item_value"><span></span> h</div></div>'
            $(ele).append(html)
            values['activ_intense'] = data.activ_intense.value
            sources['activ_intense'] = data.activ_intense.source
          }
          $(ele).height(height)
          $(ele).data('sources', sources)
          cards.withings_daily.update(panel, id, values)
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
        if (($(ele).data('entry') == 'steps') && (values['steps'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = values['steps'].toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'distance') && (values['distance'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = (values['distance']/1000).toLocaleString('de-DE', {minimumFractionDigits: 2, maximumFractionDigits: 2})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'totalcalories') && (values['totalcalories'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = values['totalcalories'].toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'activecalories') && (values['activecalories'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = values['activecalories'].toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'activ_soft') && (values['activ_soft'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = (values['activ_soft'] / 3600).toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'activ_moderate') && (values['activ_moderate'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = (values['activ_moderate'] / 3600).toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'activ_intense') && (values['activ_intense'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = (values['activ_intense'] / 3600).toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
      }
    }
  }
  if (window.cards == undefined) { window.cards = {}}
  window.cards['withings_daily'] = card
})