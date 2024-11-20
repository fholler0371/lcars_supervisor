define([], function() {
    window.modul['auth_admin'] = {
        modul: true,
        icon: '/img/mdi/account-multiple.svg',
        label: 'Konten',
        already_init : false,
        init: function () {
        },
        set_content: function() {
            let self = window.modul['auth_admin'] //content_modul_auth_admin
            if (!($('#content_modul_auth_admin').length)) {
                var html = '<div id="content_modul_auth_admin" class="content_modul"><div id="content_modul_auth_admin_splitter">'
                html += '<div id="content_modul_auth_admin_splitter_left"></div><div id="content_modul_auth_admin_splitter_right"></div></div>'
                html += '</div>'
                $(".main_content").append(html)
                require(['jqxsplitter', 'jqxlistbox', 'jqxinput', 'jqxbutton', 'jqxpasswordinput'], function() {
                    $('#content_modul_auth_admin_splitter').jqxSplitter({height: '100%', width: '100%', theme: 'material', panels: [{ size: 300, min: 150 }]})
                    $('#content_modul_auth_admin_splitter_left').append('<div id="modul_auth_admin_user_list"></div>')
                    $('#modul_auth_admin_user_list').jqxListBox({height: '100%', width: '100%', theme: 'material'})
                    $('#modul_auth_admin_user_list, #content_modul_auth_admin_splitter').css('border', 0)
                    var html = '<table style="border-collapse: collapse; margin-left: 10px"><tr><td style="height: 16px"></td></tr><tr><td>Neuer Nutzer: </td>'
                    html += '<td><input typ="text" id="auth_admin_user_new"></td>'
                    html += '<td></td><td><input type="button" value="Hinzufügen" id="auth_admin_user_add" /></td></tr><tr><td>Nutzer löschen</td>'
                    html += '<td></td><td></td><td><input type="button" value="Löschen" id="auth_admin_user_del" /></td></tr>'
                    html += '<tr style="border-bottom: 1pt solid #99c"><td style="height: 4px"></td></tr><tr><td style="height: 16px"></td></tr>'
                    html += '<tr><td>Name: </td><td><input typ="text" id="auth_admin_user_name"></td><td></td><td></td></tr>'
                    html += '<tr><td style="height: 16px"></td></tr><tr><td>E-Mail: </td>'
                    html += '<td><input typ="text" id="auth_admin_user_mail"></td><td></td><td>'
                    html += '<input type="button" value="Aktualiesieren" id="auth_admin_rec_send" />'
                    html += '</td></tr><tr style="border-bottom: 1pt solid #99c"><td style="height: 4px"></td></tr><tr><td style="height: 16px"></td></tr>'
                    html += '<tr><td>Passwort: </td><td><input type="password" id="auth_admin_user_password"></td><td></td><td>'
                    html += '<input type="button" value="Senden" id="auth_admin_password_send" /></td></tr><tr><td>MFA: </td><td colspan="2" id="auth_admin_token"></td>'
                    html += '<td><input type="button" value="Erstellen" id="auth_admin_sec" /></td></tr><tr style="border-bottom: 1pt solid #99c">'
                    html += '<td style="height: 4px"></td></tr><tr><td></td><td>Standard</td><td>mit MFA</td><td></td><tr><td style="vertical-align: top">Rechte: </td>'
                    html += '<td><div id="auth_admin_rights"></div></td><td><div id="auth_admin_rights_sec"></div></td><td style="vertical-align: bottom">'
                    html += '<input type="button" value="Senden" id="auth_admin_rights_send" /></td></tr></tr></table>'
                    $('#content_modul_auth_admin_splitter_right').append(html)                
                    $('#auth_admin_user_new').jqxInput({placeHolder: "Nutzerkürzel", height: 30, width: 200, minLength: 1, theme: 'material' })
                    $("#auth_admin_user_add, #auth_admin_user_del, #auth_admin_rec_send, #auth_admin_password_send, "+ 
                      "#auth_admin_sec, #auth_admin_rights_send")
                        .jqxButton({ width: 120, height: 40, theme: 'material' })
                    $('#auth_admin_user_name').jqxInput({placeHolder: "Name", height: 30, width: 200, minLength: 1, theme: 'material' })
                    $('#auth_admin_user_mail').jqxInput({placeHolder: "E-Mail", height: 30, width: 200, minLength: 1, theme: 'material' })
                    $('#auth_admin_user_password').jqxPasswordInput({placeHolder: "Passwort", height: 30, width: 200, minLength: 1, theme: 'material' })
                    $('#auth_admin_rights, #auth_admin_rights_sec').jqxListBox({height: 300, width: 200, checkboxes: true, theme: 'material'})
                    $('#modul_auth_admin_user_list').on('change', function (event) {
                        var args = event.args;
                        if (args) {
                          var item = args.item
                          var label = item.label
                          window.api_call(url='admin/get_user', data={name: label}).then(resp => {
                            if (resp.ok) {
                                if (resp.label != null) {
                                    $('#auth_admin_user_name').jqxInput('val', resp.label)  
                                } else {
                                    $('#auth_admin_user_name').jqxInput('val', '')
                                }
                                if (resp.mail != null) {
                                    $('#auth_admin_user_mail').jqxInput('val', resp.mail)  
                                } else {
                                    $('#auth_admin_user_mail').jqxInput('val', '')
                                }
                                $('#auth_admin_rights, #auth_admin_rights_sec').jqxListBox('clear')
                                for (var i=0; i<resp.rights_avail.length; i++) {
                                    $('#auth_admin_rights, #auth_admin_rights_sec').jqxListBox('addItem', resp.rights_avail[i])
                                }
                                for (var i=0; i<resp.rights.length; i++) {
                                    var item = $('#auth_admin_rights').jqxListBox('getItem', resp.rights[i])
                                    $('#auth_admin_rights').jqxListBox('checkItem', item )
                                }
                                for (var i=0; i<resp.rights_sec.length; i++) {
                                    var item = $('#auth_admin_rights_sec').jqxListBox('getItem', resp.rights_sec[i])
                                    $('#auth_admin_rights_sec').jqxListBox('checkItem', item )
                                }
                                $('#auth_admin_token').text('')
                            }
                          })  
                        }
                    })
                    $('#auth_admin_user_add').on('click', function()  {
                        var name = $('#auth_admin_user_new').jqxInput('val')
                        var item = $('#modul_auth_admin_user_list').jqxListBox('getItemByValue', name)
                        if (item == undefined && name != '') {
                            window.api_call(url='admin/user_add', data={name: name}).then(resp => {
                                if (resp.ok) {
                                    $('#modul_auth_admin_user_list').jqxListBox('addItem', name)
                                    $('#modul_auth_admin_user_list').jqxListBox('selectIndex', $('#modul_auth_admin_user_list').jqxListBox('getItems').length-1)
                                }
                            })
                        }
                    })
                    $('#auth_admin_user_del').on('click', function()  {
                        var name = $('#modul_auth_admin_user_list').jqxListBox('getSelectedItem').label
                        window.api_call(url='admin/user_del', data={name: name}).then(resp => {
                            if (resp.ok) {
                                $("#modul_auth_admin_user_list").jqxListBox('removeItem', name)
                                $('#modul_auth_admin_user_list').jqxListBox('selectIndex', 0 )
                            }
                        })
                    })
                    $('#auth_admin_rec_send').on('click', function() {
                        var name = $('#modul_auth_admin_user_list').jqxListBox('getSelectedItem').label,
                            label = $('#auth_admin_user_name').jqxInput('val'),
                            mail = $('#auth_admin_user_mail').jqxInput('val')
                        window.api_call(url='admin/user_edit', data={name: name, label: label, mail: mail}).then(resp => {
                            if (resp.ok) {
                            }
                        })
                    })
                    $('#auth_admin_password_send').on('click', function() {
                        var name = $('#modul_auth_admin_user_list').jqxListBox('getSelectedItem').label,
                            password = $('#auth_admin_user_password').jqxPasswordInput('val')
                        if (password.length > 6) {
                            window.api_call(url='admin/set_password', data={name: name, password: password}).then(resp => {
                            })
                        }       
                    })
                    $('#auth_admin_sec').on('click', function() {
                        var name = $('#modul_auth_admin_user_list').jqxListBox('getSelectedItem').label
                        console.log('#auth_admin_sec', name)
                        window.api_call(url='admin/mfa', data={name: name}).then(resp => {
                            if (resp.ok) {
                                $('#auth_admin_token').text(resp.token)
                            }
                        })
                        // postData('/api', { 'action': 'user_sec', 'name': name}, token=true).then(data => {
                        //   if (data.error != null) {
                        //     console.error(data)
                        //   } else {
                        //     console.log(data)
                        //     require(['qrious', 'jqxwindow'], function(qrious) {
                        //       if (!($('#auth_manger_sec_window').length)) {
                        //         $('body').append('<div id="auth_manger_sec_window"><div><span>MFA-Code</span></div><div><canvas id="auth_manger_sec_window_code"></canvas></div></div')
                        //         $('#auth_manger_sec_window').jqxWindow({width:225, height: 280, modalOpacity: 0.7, isModal: true, resizable: false, theme: 'material'})
                        //       }
                        //       $('#auth_manger_sec_window').show()
                        //       var q = new qrious({
                        //         element: $('#auth_manger_sec_window_code')[0],
                        //         value: data.mfa,
                        //         size: 200
                        //       })
                        //       console.log(q)
                        //     })
                        //   }
                        // })
                    })
                    $('#auth_admin_rights_send').on('click', function() {
                        var name = $('#modul_auth_admin_user_list').jqxListBox('getSelectedItem').label,
                            rights = [],
                            rights_sec = []
                        var entries = $('#auth_admin_rights').jqxListBox('getCheckedItems')
                        for (var i=0; i<entries.length; i++) {
                          rights.push(entries[i].label)
                        }
                        var entries = $('#auth_admin_rights_sec').jqxListBox('getCheckedItems')
                        for (var i=0; i<entries.length; i++) {
                          rights_sec.push(entries[i].label)
                        }
                        window.api_call(url='admin/set_apps', data={name: name, apps: rights, apps_sec: rights_sec}).then(resp => {
                            // console.log(name, rights, rights_sec)
                        })
                    })
                    self.load_users()                  
                })
            } else {
                self.load_users()
            }
            $('#content_modul_auth_admin').show()
        },
        show: function () {
            let self = window.modul['auth_admin']
            window.modul['helper'].activate('auth_admin', self.label)
            self.set_content()
        },
        stop: function() {
        
        },
        load_users: function() {
            window.api_call(url='admin/get').then(resp => {
                if (resp.ok) {
                    $('#modul_auth_admin_user_list').jqxListBox('clear')
                    let data = resp.data.data
                    for (var i=0; i<data.length; i++) {
                        $('#modul_auth_admin_user_list').jqxListBox('addItem', data[i])
                    }
                    if (data.length > 0) {
                        $('#modul_auth_admin_user_list').jqxListBox('selectIndex', 0 )
                    }
                }
            })
        }
    }
    window.modul['auth_admin'].init()
});