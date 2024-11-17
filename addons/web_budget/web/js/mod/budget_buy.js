define([], function() {
    window.modul['budget_buy'] = {
        modul: true,
        icon: '/css/images/playlist_plus.svg',
        label: 'Ausgaben',
        already_init : false,
        edit_run : false,
        init: function () {
        },
        set_content: function() {
          let self = window.modul['budget_buy']
          if (!($('#content_modul_budget_buy').length)) {
            var html = '<div id="content_modul_budget_buy" class="content_modul jqx-widget-content-material"><div id="content_modul_budget_buy_grid">'
            $(".main_content").append(html)
            require([ 'jqxdatetimeinput', 'jqxdropdownlist', 'jqxgrid_selection', 'jqxgrid_edit'], function() {                                        
              var source = {
                datatype: "json",
                datafields: [
                  { name: 'id', type: 'int'},
                  { name: 'date', type: 'date' },
                  { name: 'category', type: 'string' },
                  { name: 'name', type: 'string' },
                  { name: 'amount', type: 'float' },
                  { name: 'count', type: 'int' }
                ],
                updaterow: function (rowid, rowdata, commit) {
                  console.log(rowdata)
                  var xid = -1
                  if (rowdata.id != undefined) {
                    xid = rowdata.id
                  }
                  var out = {'amount': rowdata.amount, 'id': xid, 'category': rowdata.category, count: rowdata.count, name: rowdata.name}
                  var d = "0"+rowdata.date.getDate()
                  var m = "0"+(rowdata.date.getMonth()+1)
                  out['date'] = rowdata.date.getFullYear() + '-' + m.slice(-2) + '-' + d.slice(-2)
                  if (!self.edit_run) {
                    self.edit_run = true
                    window.api_call(url='budget/buy_edit', data=out).then(resp => {
                      if (resp.ok) {
                        let data = resp.data.data
                        if (data.id != xid) {
                          var index = $('#content_modul_budget_buy_grid').jqxGrid('getrowboundindexbyid', rowid)
                          $("#content_modul_budget_buy_grid").jqxGrid('setcellvalue', index, "id", data.id)
                        }
                        commit(true)
                      }
                      self.edit_run = false
                    })
                  }
                },
                id: 'id',
                url: 'api'
              }
              var dataAdapter = new $.jqx.dataAdapter(source, {
                loadServerData: function (serverdata, source, callback) {
                  window.api_call(url='budget/buy_get').then(resp => {
                    if (resp.ok) {
                      let data = resp.data.data
                      for (var i=0; i<data.list.length; i++) {
                        data.list[i].date = new Date(data.list[i].date)
                      }
                      self.categories = data.categories
                      self.names = data.names
                      callback({records:data.list})
                    }
                  })
                }
              })
              $("#content_modul_budget_buy_grid").jqxGrid({
                width: '100%',
                height: '100%',
                source: dataAdapter, 
                theme: 'material',  
                showstatusbar: true,   
                renderstatusbar: function(statusbar) {
                  let container = $("<div style='margin: 5px;'></div>")
                  let img = '<img id="content_modul_budget_buy_grid_add" src="/img/mdi/plus.svg" class="button_32" style="position: relative; top: -3px; cursor:pointer"></img>'
                  let rightSpan = $(`<span style='float: right; margin-right: 11px;'>${img}</span>`)
                  container.append(rightSpan)
                  img = '<img id="content_modul_budget_buy_grid_refresh" src="/img/mdi/refresh.svg" class="button_32" style="position: relative; top: -3px; cursor:pointer"></img>'
                  rightSpan = $(`<span style='float: right; margin-right: 11px;'>${img}</span>`)
                  container.append(rightSpan)
                  statusbar.append(container)
                  $('#content_modul_budget_buy_grid_add').off('click')
                  $('#content_modul_budget_buy_grid_add').on('click', function() {
                    $('#content_modul_budget_buy_grid').jqxGrid('addrow', null, 
                                                                  {id: -1, date: new Date(),
                                                                    category: self.categories[0],
                                                                    text: '', amount: 0, count: 0}, 'first')
                  })
                  $('#content_modul_budget_buy_grid_refresh').off('click')
                  $('#content_modul_budget_buy_grid_refresh').on('click', function() {
                    $("#content_modul_budget_buy_grid").jqxGrid('updatebounddata')
                  })
                },
                localization: {
                  patterns: {
                    d: "dd.MM.yyyy",
                  },
                  currencysymbol: "€",
                  currencysymbolposition: "after",
                  decimalseparator: ',',
                  thousandsseparator: '.',
                  loadtext: "Loading...",
                  emptydatastring: "keine Daten angezeigt",
                  firstDay: 1,
                  "/": ".",
                  days: {
                    namesShort: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
                    namesAbbr: ["Sonn", "Mon", "Dien", "Mitt", "Donn", "Fre", "Sams"],
                    names: ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"]
                  },
                  months: {
                    names: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember", ""],
                    namesAbbr: ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dez", ""]
                  }
                },       
                editable: true,
                columns: [
                  {'text': 'id', datafield: 'id', hidden: true},
                  { text: 'Datum', datafield: 'date', cellsalign: 'right', align: 'left', width: 200, cellsformat: 'd', columntype: 'datetimeinput'},
                  { text: 'Kategorie', datafield: 'category', columntype: 'dropdownlist', width: 200,
                    createeditor: function (row, cellvalue, editor, celltext, cellwidth, cellheight) {
                      editor.jqxDropDownList({source: self.categories })
                  }},
                  { text: 'Bezeichnung', datafield: 'name', columntype: 'combobox',
                    createeditor: function (row, cellvalue, editor, celltext, cellwidth, cellheight) {
                      editor.jqxComboBox({source: self.names, searchMode: 'containsignorecase'})
                  }},
                  { text: 'Betrag', datafield: 'amount', align: 'left', cellsalign: 'right', cellsformat: 'c2', width: 200},
                  { text: 'Anzahl', datafield: 'count', align: 'left', cellsalign: 'right', cellsformat: 'f0', width: 200}
                ]
              })
            })
          }
        },
        show: function () {
            let self = window.modul['budget_buy']
            window.modul['helper'].activate('budget_buy', self.label)
            self.set_content()
            $('#content_modul_budget_buy').show()
        },
        stop: function() {
        
        }
    }
    window.modul['budget_buy'].init()
});
