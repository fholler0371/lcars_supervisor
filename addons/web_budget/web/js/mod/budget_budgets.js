define([], function() {
    window.modul['budget_budgets'] = {
        modul: true,
        icon: '/css/images/cash.svg',
        label: 'Budgets',
        already_init : false,
        init: function () {
        },
        set_content: function() {
          let self = window.modul['budget_budgets']
          if (!($('#content_modul_budget_budgets').length)) {
            var html = '<div id="content_modul_budget_budgets" class="content_modul jqx-widget-content-material"><div id="content_modul_budget_time_grid">'
            $(".main_content").append(html)
            require([ 'jqxdatetimeinput', 'jqxdropdownlist', 'jqxgrid_selection', 'jqxgrid_edit'], function() {                                        
              let source = {
                datatype: "json",
                datafields: [
                  { name: 'category', type: 'string' },
                  { name: 'start', type: 'date' },
                  { name: 'end', type: 'date' },
                  { name: 'amount', type: 'float' }
                ],
                updaterow: function (rowid, rowdata, commit) {
                  var out = {'amount': rowdata.amount, 'id': rowdata.id, 'category': rowdata.category}
                  var d = "0"+rowdata.start.getDate()
                  var m = "0"+(rowdata.start.getMonth()+1)
                  out['start'] = rowdata.start.getFullYear() + '-' + m.slice(-2) + '-' + d.slice(-2)
                  var d = "0"+rowdata.end.getDate()
                  var m = "0"+(rowdata.end.getMonth()+1)
                  out['end'] = rowdata.end.getFullYear() + '-' + m.slice(-2) + '-' + d.slice(-2)
                  window.api_call(url='budget/budget_edit', data=out).then(resp => {
                    if (resp.ok) {
                    }
                  })
                },
                id: 'id',
                url: 'api'
              }
              var dataAdapter = new $.jqx.dataAdapter(source, {
                loadServerData: function (serverdata, source, callback) {
                  window.api_call(url='budget/get_all').then(resp => {
                    if (resp.ok) {
                      let data = resp.data.data
                      for (var i=0; i<data.length; i++) {
                        data[i].start = new Date(data[i].start)
                        data[i].end = new Date(data[i].end)
                      }
                      self._cat_data = data
                      callback({records:data})
                    }
                  })
                }
              })
              $("#content_modul_budget_time_grid").jqxGrid({
                width: '100%',
                height: '100%',
                source: dataAdapter, 
                theme: 'material',  
                showstatusbar: true,   
                renderstatusbar: function(statusbar) {
                  let container = $("<div style='margin: 5px;'></div>")
                  let img = '<img id="content_modul_budget_time_grid_add" src="/img/mdi/plus.svg" class="button_32" style="position: relative; top: -3px; cursor:pointer"></img>'
                  let rightSpan = $(`<span style='float: right; margin-right: 11px;'>${img}</span>`)
                  container.append(rightSpan)
                  img = '<img id="content_modul_budget_time_grid_refresh" src="/img/mdi/refresh.svg" class="button_32" style="position: relative; top: -3px; cursor:pointer"></img>'
                  rightSpan = $(`<span style='float: right; margin-right: 11px;'>${img}</span>`)
                  container.append(rightSpan)
                  statusbar.append(container)
                  $('#content_modul_budget_time_grid_add').off('click')
                  $('#content_modul_budget_time_grid_add').on('click', function() {
                    window.api_call(url='budget/get_new').then(resp => {
                      if (resp.ok) {
                        data = resp.data.data
                        data['start'] = new Date(data['start'])
                        data['end'] = new Date(data['end'])
                        $('#content_modul_budget_time_grid').jqxGrid('addrow', null, data)
                      }
                    })
                  })
                  $('#content_modul_budget_time_grid_refresh').off('click')
                  $('#content_modul_budget_time_grid_refresh').on('click', function() {
                    $("#content_modul_budget_time_grid").jqxGrid('updatebounddata')
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
                  loadtext: "Laden...",
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
                  { text: 'Kategorie', datafield: 'category', columntype: 'dropdownlist', 
                    createeditor: function (row, cellvalue, editor, celltext, cellwidth, cellheight) {
                      editor.jqxDropDownList({source: window.modul.budget_time.categories })
                  }},
                  { text: 'Beginn', datafield: 'start', cellsalign: 'right', align: 'left', width: 200, cellsformat: 'd', columntype: 'datetimeinput'},
                  { text: 'Ende', datafield: 'end', cellsalign: 'right', align: 'left', width: 200, cellsformat: 'd', columntype: 'datetimeinput'},
                  { text: 'pro Monat', datafield: 'amount', align: 'left', cellsalign: 'right', cellsformat: 'c2', width: 200}
                ]
              })
            })
          }
        },
        show: function () {
            let self = window.modul['budget_budgets']
            window.modul['helper'].activate('budget_budgets', self.label)
            self.set_content()
            $('#content_modul_budget_budgets').show()
        },
        stop: function() {
        
        }
    }
    window.modul['budget_budgets'].init()
});

// define(function () {
//   var _modul = {
//     icon: '/js/img/mdi/cash.svg',
//     already_init : false,
//     label: 'Bugets',
//     categories: [],
//     init: function() {
//       if (!modul.budget_time.already_init) {
//         modul.budget_time.already_init = true
//       }
//     },
//     show: function() {
//       console.log('show budget_time')
//       $('#header_appname').text(modul.budget_time.label)
//       require([ 'jqxdatetimeinput', 'jqxdropdownlist', 'jqxgrid.selection', 'jqxgrid.edit'], function() {
//         if (!($('#content_modul_budget_time').length)) {
//         }
//         $('#content_modul_budget_time').show()
//       })
//     }
//   }
//   window.modul.budget_time = _modul
//   console.log("budget_time")
//   return _modul
// })
  