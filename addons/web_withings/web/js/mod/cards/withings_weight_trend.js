define(function () {
    var card = {
      create : function(panel, label, id, _) {
        var html = '<div class="sh_card" data-panel="'+panel+'" data-id="'+id+'" data-type="withings_weight_trend"><div class="sh_card_label">'+label+'</div></div>'
        $('#content_modul_page_'+panel).append(html)
        window.api_call(url='sm/cards_source', data={'panel': panel, 'card': id,
                                                     'items': ['gewicht_month', 'gewicht_quartal', 'gewicht_year']}).then(resp => {
          if (resp.ok) {
            let data = resp.data
            var height = 32
            var values = {}
            var sources = {}
            var ele = $('#content_modul_page_'+panel).children()[id]
            if (data.gewicht_month != null && data.gewicht_month.value != null) {
              height += 24
              var html = '<div data-entry="gewicht_month">'
              html += '<span class="sh_card_item_labels"  style="left: 5px; position: relative">Monat</span>'
              html += '<div class="sh_card_item_value"><span></span> kg</div></div>'
              $(ele).append(html)
              values['gewicht_month'] = data.gewicht_month.value
              sources['gewicht_month'] = data.gewicht_month.source
            }
            if (data.gewicht_quartal != null && data.gewicht_quartal.value != null) {
              height += 24
              var html = '<div data-entry="gewicht_quartal">'
              html += '<span class="sh_card_item_labels"  style="left: 5px; position: relative">Quartal</span>'
              html += '<div class="sh_card_item_value"><span></span> kg</div></div>'
              $(ele).append(html)
              values['gewicht_quartal'] = data.gewicht_quartal.value
              sources['gewicht_quartal'] = data.gewicht_quartal.source
            }
            if (data.gewicht_year != null && data.gewicht_year.value != null) {
              height += 24
              var html = '<div data-entry="gewicht_year">'
              html += '<span class="sh_card_item_labels"  style="left: 5px; position: relative">Jahr</span>'
              html += '<div class="sh_card_item_value"><span></span> kg</div></div>'
              $(ele).append(html)
              values['gewicht_year'] = data.gewicht_year.value
              sources['gewicht_year'] = data.gewicht_year.source
            }
            $(ele).height(height)
            $(ele).data('sources', sources)
            cards.withings_weight_trend.update(panel, id, values)
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
          if (($(ele).data('entry') == 'gewicht_month') && (values['gewicht_month'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['gewicht_month'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'gewicht_quartal') && (values['gewicht_quartal'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['gewicht_quartal'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'gewicht_year') && (values['gewicht_year'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['gewicht_year'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
        }
      }
    }
    if (window.cards == undefined) { window.cards = {}}
    window.cards['withings_weight_trend'] = card
  })