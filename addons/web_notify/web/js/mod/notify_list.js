define([], function() {
    window.modul['notify_list'] = {
        modul: true,
        icon: '/img/mdi/information-variant.svg',
        label: 'Meldungen',
        already_init : false,
        data_loading : false,
        remove_timer : null,
        relod_timer : null,
        init: function () {
        },
        set_content: function() {
            let self = window.modul['notify_list']
            if (!($('#content_modul_budget_net').length)) {
                var html = '<div id="content_modul_notify_list" class="content_modul jqx-widget-content-material"><div id="content_modul_notify_list_list">'
                $(".main_content").append(html)
                var source = {
                    datatype: "json",
                    datafields: [
                      { name: 'app', type: 'string'},
                      { name: 'app_name', type: 'string'},
                      { name: 'app_icon', type: 'string'},
                      { name: 'type', type: 'string' },
                      { name: 'text', type: 'string' },
                      { name: 'md5', type: 'string' },
                      { name: 'timestamp', type: 'int' }
                    ],
                    id: 'md5',
                    url: 'api'
                }
                require(['jqxlistbox'], function() {
                  var dataAdapter = new $.jqx.dataAdapter(source, {
                    loadServerData: function (serverdata, source, callback) {
                      if (!self.data_loading) {
                        self.data_loading = true
                        window.api_call(url='notify/get_list').then(resp => {
                          if (resp.ok) {
                            if (resp.data != null) {
                              self.data = resp.data.data
                              callback({records:resp.data.data})
                            }
                          }
                          self.data_loading = false
                        })
                      }
                    }
                  })
                  $("#content_modul_notify_list_list").jqxListBox({ 
                    displayMember: "text", 
                    valueMember: "md5", 
                    width: '100%',
                    height: '100%',
                    source: dataAdapter, 
                    theme: 'material',
                    checkboxes: true,
                    renderer: function (index, label, value) {
                      let color = ' var(--main-color_be)'
                      let icon = 'information-box-outline'
                      let entry = self.data[index]
                      let app_icon = entry.app_icon
                      let app_name = entry.app_name
                      if (entry.type == 'warn') {
                        color = ' var(--main-color_gr)'
                        icon = 'close-box-outline'
                      }
                      let cross = ''
                      let html = '<div style="border: 1px solid'+ color +'; border-radius: 8px;"><table style="width: 100%; color:'+ color +'"><tr><td width="40px">' 
                      html += '<img src="/img/mdi/'+icon+'.svg" style="height:32px" onload="SVGInject(this)"></td><td width="calc( 100% - 32px )">'
                      html += '<span style="font-size:70%">'+app_name+'</span></br>'+label + '</td><td style="width: 20px;vertical-align: top">'
                      html += cross + '</td><td width="40px"><img src="'
                      html += app_icon+'" style="height:32px" onload="SVGInject(this)"></td><tr><table></div>'
                      return html
                    }
                  })
                  $("#content_modul_notify_list_list").css('border', 'none')
                })
            } 
        },
        show: function () {
            let self = window.modul['notify_list']
            window.modul['helper'].activate('notify_list', self.label)
            self.set_content()
            $('#content_modul_notify_list').show()
            self.data_loading = false
            self.remove_timer = setInterval(self.clear, 2000) 
            self.relod_timer = setInterval(self.reload, 300000) 
 	      },
        stop: function() {
          let self = window.modul['notify_list']
          clearInterval(self.remove_timer)
          clearInterval(self.reload_timer)
        },
        clear : function() {
          let self = window.modul['notify_list']
          if (!self.data_loading) {
            let selected = $("#content_modul_notify_list_list").jqxListBox('getCheckedItems')
            if (selected.length > 0) {
              self.data_loading = true
              let item = selected[0]
              window.api_call(url='notify/remove', data={md5: item.value}).then(resp => {
                if (resp.ok) {
                  console.info('Eintrag entfernt ')
                }
                self.data_loading = false
                $("#content_modul_notify_list_list").jqxListBox('refresh')
              })
            }
          }
        },
        reload: function() {
          console.log('reload')
          $("#content_modul_notify_list_list").jqxListBox('refresh')
        }
    }
    window.modul['notify_list'].init()
});
