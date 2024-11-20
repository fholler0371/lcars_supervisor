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
                    html += '<input type="button" value="Senden" id="auth_admin_password_send" /></td></tr><tr><td>MFA: </td><td></td><td></td>'
                    html += '<td><input type="button" value="Erstellen" id="auth_admin_mfa" /></td></tr><tr style="border-bottom: 1pt solid #99c">'
                    html += '<td style="height: 4px"></td></tr><tr><td></td><td>Standard</td><td>mit MFA</td><td></td><tr><td style="vertical-align: top">Rechte: </td>'
                    html += '<td><div id="auth_admin_rights"></div></td><td><div id="auth_admin_rights_mfa"></div></td><td style="vertical-align: bottom">'
                    html += '<input type="button" value="Senden" id="auth_admin_rights_send" /></td></tr></tr></table>'
                    $('#content_modul_auth_admin_splitter_right').append(html)                
                    $('#auth_admin_user_new').jqxInput({placeHolder: "Nutzerkürzel", height: 30, width: 200, minLength: 1, theme: 'material' })
                    $("#auth_admin_user_add, #auth_admin_user_del, #auth_admin_rec_send, #auth_admin_password_send, "+ 
                      "#auth_admin_mfa, #auth_admin_rights_send")
                        .jqxButton({ width: 120, height: 40, theme: 'material' })
                    $('#auth_admin_user_name').jqxInput({placeHolder: "Name", height: 30, width: 200, minLength: 1, theme: 'material' })
                    $('#auth_admin_user_mail').jqxInput({placeHolder: "E-Mail", height: 30, width: 200, minLength: 1, theme: 'material' })
                    $('#auth_admin_user_password').jqxPasswordInput({placeHolder: "Passwort", height: 30, width: 200, minLength: 1, theme: 'material' })
                    $('#auth_admin_rights, #auth_admin_rights_mfa').jqxListBox({height: 300, width: 200, checkboxes: true, theme: 'material'})
                    $('#modul_auth_admin_user_list').on('change', function (event) {
                        var args = event.args;
                        if (args) {
                          var item = args.item
                          var label = item.label
                          console.log(label)
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
                                $('#auth_admin_rights, #auth_admin_rights_mfa').jqxListBox('clear')
                                for (var i=0; i<resp.rights_avail.length; i++) {
                                    $('#auth_admin_rights, #auth_admin_rights_mfa').jqxListBox('addItem', resp.rights_avail[i])
                                }
                            }
                          })  
                        //       for (var i=0; i<data.rights.length; i++) {
                        //         var item = $('#auth_admin_rights').jqxListBox('getItem', data.rights[i])
                        //         $('#auth_admin_rights').jqxListBox('checkItem', item )
                        //       }
                        //       for (var i=0; i<data.rights_mfa.length; i++) {
                        //         var item = $('#auth_admin_rights_mfa').jqxListBox('getItem', data.rights_mfa[i])
                        //         $('#auth_admin_rights_mfa').jqxListBox('checkItem', item )
                        //       }
                        }
                    })
                    $('#auth_admin_user_del').on('click', function()  {
                        var name = $('#modul_auth_admin_user_list').jqxListBox('getSelectedItem').label
                        // postData('/api', { 'action': 'user_del', 'user': name }, token=true).then(data => {
                        //   if (data.error != null) {
                        //     console.error(data)
                        //   } else {
                        //     if (data.ok) {
                        //       $("#modul_auth_admin_user_list").jqxListBox('removeItem', name)
                        //       $('#modul_auth_admin_user_list').jqxListBox('selectIndex', 0 )
                        //     }
                        //   }
                        // })
                    })
                    $('#auth_admin_rec_send').on('click', function() {
                        var name = $('#modul_auth_admin_user_list').jqxListBox('getSelectedItem').label,
                            firstname = $('#auth_admin_user_firstname').jqxInput('val'),
                            lastname = $('#auth_admin_user_lastname').jqxInput('val'),
                            mail = $('#auth_admin_user_mail').jqxInput('val')
                        // postData('/api', { 'action': 'user_rec_set', 'name': name, 'firstname': firstname, 
                        //                                              'lastname': lastname, 'mail': mail }, token=true).then(data => {
                        //   if (data.error != null) {
                        //     console.error(data)
                        //   }
                        // })
                    })
                    $('#auth_admin_password_send').on('click', function() {
                        var name = $('#modul_auth_admin_user_list').jqxListBox('getSelectedItem').label,
                            password = $('#auth_admin_user_password').jqxPasswordInput('val')
                        // postData('/api', { 'action': 'user_password', 'name': name, 'password': password}, token=true).then(data => {
                        //   if (data.error != null) {
                        //     console.error(data)
                        //   }
                        // })
                    })
                    $('#auth_admin_mfa').on('click', function() {
                        var name = $('#modul_auth_admin_user_list').jqxListBox('getSelectedItem').label
                        // postData('/api', { 'action': 'user_mfa', 'name': name}, token=true).then(data => {
                        //   if (data.error != null) {
                        //     console.error(data)
                        //   } else {
                        //     console.log(data)
                        //     require(['qrious', 'jqxwindow'], function(qrious) {
                        //       if (!($('#auth_manger_mfa_window').length)) {
                        //         $('body').append('<div id="auth_manger_mfa_window"><div><span>MFA-Code</span></div><div><canvas id="auth_manger_mfa_window_code"></canvas></div></div')
                        //         $('#auth_manger_mfa_window').jqxWindow({width:225, height: 280, modalOpacity: 0.7, isModal: true, resizable: false, theme: 'material'})
                        //       }
                        //       $('#auth_manger_mfa_window').show()
                        //       var q = new qrious({
                        //         element: $('#auth_manger_mfa_window_code')[0],
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
                            rights_mfa = []
                        var entries = $('#auth_admin_rights').jqxListBox('getCheckedItems')
                        for (var i=0; i<entries.length; i++) {
                          rights.push(entries[i].label)
                        }
                        var entries = $('#auth_admin_rights_mfa').jqxListBox('getCheckedItems')
                        for (var i=0; i<entries.length; i++) {
                          rights_mfa.push(entries[i].label)
                        }
                        // postData('/api', { 'action': 'user_rights_set', 'name': name, rights: rights, rights_mfa: rights_mfa}, token=true).then(data => {
                        //   if (data.error != null) {
                        //     console.error(data)
                        //   }
                        // })
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