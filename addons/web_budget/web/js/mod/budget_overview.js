define([], function() {
    window.modul['budget_overview'] = {
        modul: true,
        icon: '/css/images/finance.svg',
        label: 'Übersicht',
        already_init : false,
        init: function () {
        },
        set_content: function() {
            let self = window.modul['router_net']
            if (!($('#content_modul_budget_net').length)) {
                var html = '<div id="content_modul_budget_status" class="content_modul jqx-widget-content-material"><div id="content_modul_budget_status_grid">'
                $(".main_content").append(html)
                var source = {
                    datatype: "json",
                    datafields: [
                      { name: 'id', type: 'int'},
                      { name: 'category', type: 'string' },
                      { name: 'saldo', type: 'float' },
                      { name: 'payed', type: 'float' },
                      { name: 'days', type: 'int' }
                    ],
                    id: 'id',
                    url: 'api'
                }
                require(['jqxgrid_selection'], function() {
                    var dataAdapter = new $.jqx.dataAdapter(source, {
                        loadServerData: function (serverdata, source, callback) {
                            window.api_call(url='budget/get_status').then(resp => {
                                if (resp.ok) {
                                    callback({records:resp.data.data})
                                }
                            })
                        }
                    })
                    $('head').append($('<style>.modul_budget_status_grid_state_1 {color: var(--main-color_gr);}</style>'))
                    $('head').append($('<style>.modul_budget_status_grid_state_2 {color: var(--main-color_pl);}</style>'))
                    var cellclass = function (row, columnfield, value){
                        var rowData = $("#content_modul_budget_status_grid").jqxGrid('getrowdata', row)
                        if (rowData.saldo > 0) {
                          return 'modul_budget_status_grid_state_1'
                        } else if (rowData.days <= rowData.days_info) {
                          return 'modul_budget_status_grid_state_2'
                        }
                        return '' 
                    } 
                    $("#content_modul_budget_status_grid").jqxGrid({
                        width: '100%',
                        height: '100%',
                        source: dataAdapter, 
                        theme: 'material',  
                        showstatusbar: true,   
                        renderstatusbar: function(statusbar) {
                            statusbar.text('')
                          let container = $("<div style='margin: 5px;'></div>")
                          img = '<img id="content_modul_budget_status_grid_refresh" src="/img/mdi/refresh.svg" class="button_32" style="position: relative; top: -3px; cursor:pointer"></img>'
                          rightSpan = $(`<span style='float: right; margin-right: 11px;'>${img}</span>`)
                          container.append(rightSpan)
                          statusbar.append(container)
                          $('#content_modul_budget_status_grid_refresh').off('click')
                          $('#content_modul_budget_status_grid_refresh').on('click', function() {
                            $("#content_modul_budget_status_grid").jqxGrid('updatebounddata')
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
                        columns: [
                          {'text': 'id', datafield: 'id', hidden: true},
                          { text: 'Kategorie', datafield: 'category', cellclassname: cellclass},
                          { text: 'Bilanz', datafield: 'saldo', cellsalign: 'right', cellsformat: 'c2', width: 200, cellclassname: cellclass},
                          { text: 'Ausgegeben', datafield: 'payed', cellsalign: 'right', cellsformat: 'c2', width: 200, cellclassname: cellclass},
                          { text: 'Resttage', datafield: 'days', cellsalign: 'right', cellsformat: 'f0', width: 200, cellclassname: cellclass}
                        ]
                    })
                                        
                })
            } 
        },
        show: function () {
            let self = window.modul['budget_overview']
            window.modul['helper'].activate('budget_overview', self.label)
            self.set_content()
            $('#content_modul_budget_status').show()
        },
        stop: function() {
        
        }
    }
    window.modul['budget_overview'].init()
});
