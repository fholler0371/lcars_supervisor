define([], function() {
    window.modul['budget_cat'] = {
        modul: true,
        icon: '/css/images/katalog.svg',
        label: 'Kategorien',
        already_init : false,
        init: function () {
        },
        set_content: function() {
          if (!($('#content_modul_budget_cat').length)) {
            var html = '<div id="content_modul_budget_cat" class="content_modul jqx-widget-content-material"><div id="content_modul_budget_category_splitter">'
            html += '<div id="content_modul_budget_category_splitter_left"></div><div id="content_modul_budget_category_splitter_right"></div></div>'
            html += '</div>'
            $(".main_content").append(html)
            require(['jqxsplitter', 'jqxlistbox', 'jqxinput', 'jqxcheckbox', 'jqxnumberinput', 'jqxbutton'], function() {                                        
              $('#content_modul_budget_category_splitter').jqxSplitter({height: '100%', width: '100%', theme: 'material', panels: [{ size: 300, min: 150 }]})
              $('#content_modul_budget_category_splitter_left').append('<div id="modul_budget_category_list"></div>')
              $('#modul_budget_category_list').jqxListBox({height: '100%', width: '100%', theme: 'material'})
              $('#modul_budget_category_list, #content_modul_budget_category_splitter').css('border', 0)
              html = '<table style="border-collapse: collapse; margin-left: 10px"><tr><td>Bezeichnung</td><td>Aktiv</td><td>Info-Tage</td></tr>'
              html += '<tr><td style="height: 16px"></td></tr>'
              html += '<tr><td><input type="text" id="modul_budget_category_budget"></td><td><div id="modul_budget_category_activ" style="margin-left: 10px; float: left;">'
              html += '</div></td><td><div id="modul_budget_category_days"></div></td></tr>'
              html += '<tr><td style="height: 16px"></td></tr>'
              html += '<tr><td><input type="button" value="Neu" id="modul_budget_category_new" /></td><td></td><td>'
              html += '<input type="button" value="Sichern" id="modul_budget_category_save" /></td></tr>'
              html += '</table>'
              $('#content_modul_budget_category_splitter_right').append(html)
              $('#modul_budget_category_budget').jqxInput({placeHolder: "Budget", height: 30, width: 300, minLength: 1, theme: 'material' })
              $("#modul_budget_category_activ").jqxCheckBox({ width: 120, height: 25, checked: true, theme: 'material'})
              $("#modul_budget_category_days").jqxNumberInput({ width: '75px', spinButtons: true, decimalDigits: 0, min: 0, max: 999, digits: 3, theme: 'material' })
              $("#modul_budget_category_new, #modul_budget_category_save").jqxButton({ width: 120, height: 40, theme: 'material' })
              $("#modul_budget_category_new").on('click', function() {
                window.api_call(url='category/category_new').then(resp => {
                  if (resp.ok) {
                    let found = false
                    let items = $("#modul_budget_category_list").jqxListBox('getItems')
                    data = resp.data.data
                    if (items != undefined) {
                      items.forEach(element => {
                        found = element.value.id == data.id
                      });
                    }
                    if (!found) {
                      $("#modul_budget_category_list").jqxListBox('addItem', { label: data.label, value: {'id': data.id, 'activ': data.activ, 'days': data.days}} )
                    } 
                  }
                })
              })
              $("#modul_budget_category_save").on('click', function() {
                try {
                  var item = $("#modul_budget_category_list").jqxListBox('getSelectedItem')
                } catch {
                  var item = null
                }
                if (item != null) {
                  var label = item.label
                  var activ = $("#modul_budget_category_activ").jqxCheckBox('val')
                  var days = $("#modul_budget_category_days").jqxNumberInput('val')
                  var new_label =  $('#modul_budget_category_budget').jqxInput('val')
                  $("#modul_budget_category_list").jqxListBox('updateItem', { label: new_label, value: {id: item.value.id, activ: activ, days: days}}, item)
                  rec = {label: new_label, id: item.value.id, activ: activ, days, days}
                  window.api_call(url='category/category_edit', data=rec).then(resp => {
                    if (!resp.ok) {
                      console.error(resp)
                    }
                  })
                }
              })
              $('#modul_budget_category_list').on('select', function (event) {
                var args = event.args;
                if (args) {
                  var item = args.item;
                  var originalEvent = args.originalEvent;
                      // get item's label and value.
                  $('#modul_budget_category_budget').jqxInput('val', item.label)
                  let value = item.value;
                  $("#modul_budget_category_days").jqxNumberInput('val', value.days)
                  if (value.activ) {
                    $("#modul_budget_category_activ").jqxCheckBox('check')
                  } else {
                    $("#modul_budget_category_activ").jqxCheckBox('uncheck')
                  }
                }
              })
            })
          }
          window.api_call(url='category/get_categories').then(resp => {
            if (resp.ok) {
              $("#modul_budget_category_list").jqxListBox('clear')
              let data = resp.data.data
              if (data.length > 0){
                for (let i=0; i<data.length; i++) {
                  $("#modul_budget_category_list").jqxListBox('addItem', { label: data[i].label, value: {'id': data[i].id, 'activ': data[i].activ, 'days': data[i].days}} )
                }
                $("#modul_budget_category_list").jqxListBox('selectIndex', 0 )
              }
            }
          })
        },
        show: function () {
            let self = window.modul['budget_cat']
            window.modul['helper'].activate('budget_cat', self.label)
            self.set_content()
            $('#content_modul_budget_cat').show()
        },
        stop: function() {
        
        }
    }
    window.modul['budget_cat'].init()
});
