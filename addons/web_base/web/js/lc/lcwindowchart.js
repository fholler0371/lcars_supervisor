define('lcwindowchart', ['lcwindow', 'lcbuttons'], function() {
    (function($) {
      $.lc.addFunction('lcWindowChart', init=function(ctl, options, _id){
        $(ctl).lcWindow({height: '90%', width: '90%'})
      },
      data={
        show: function(ctl, options) {
          var _options = $(ctl).data('lcWindowChart')
          if (options != undefined) {
            _options = $.extend(_options, options)
            $(ctl).data('lcWindowChart', _options)
          }
          if (_options == undefined) {
            console.error('lcWindowChart not intialized')
            return
          }
          $(ctl).lcWindow('show')
          $(ctl).lcWindow('setTitle', _options.label)
          let _id = $(ctl).attr('id')
          var buttons_labels = _options.intervalls.split(',')
          if ($('#'+_id+'_bar').length) {
            $('#'+_id+'_bar').append('<div id="'+_id+'_buttons'+'"></div>')
            console.log('need to insert')
          }
          if ($('#'+_id+'_buttons').hasClass('lcButtonBar')) {
            $('#'+_id+'_buttons').lcButtonBar('remove')
          }
          if (buttons_labels.length > 1) {
            let data = []
            for (var i=0; i<buttons_labels.length; i++) {
              let text = undefined
              switch(buttons_labels[i]) {
                case 'D':
                  text = "Tag"
                  break
                case 'W':
                  text = "Woche"
                  break
                case 'M':
                  text = "Monat"
                  break
                case 'Q':
                  text = "Quartal"
                  break
                case 'Y':
                  text = "Jahr"
                  break
                case 'A':
                  text = "Alles"
                  break
                default:
                  text = undefined
                  break
              }
              data.push({data: {interval: buttons_labels[i]}, text: text})
            }  
            $('#'+_id+'_buttons').lcButtonBar({buttons: data, btn_fn: function(event) {
                var interval = $(event.currentTarget).data('interval')
                $($(event.currentTarget).closest('.lcWindowChart')).lcWindowChart('load', interval)
              }
            })
            var t = $(ctl).data('lcWindowChart_timer')
            if (t) {
              try {
                clearTimeout(t)
              } catch {}
            }
            t = setTimeout($.lcWindowChart._close, 120000, ctl)
            $(ctl).data('lcWindowChart_timer', t)
          }
          $.lcWindowChart._load(ctl, _options.interval)
        },
        close: function(ctl) {
          $(ctl).lcWindow('close')
        },
        load: function(ctl, interval) {
          var _options = $(ctl).data('lcWindowChart')
          window.api_call(url='sm/history_chart_data', data={'interval': interval, 'sensor': _options.sensor}).then(resp => {
            if (resp.ok) {
              let data = resp.data
              require(['highcharts/highcharts'], function(Highcharts) {
                let _id = $(ctl).attr('id')
                series = []
                for (var i=0; i<data.length; i++) {
                  for (var j=0; j<data[i].data.length; j++) {
                    data[i].data[j] = [data[i].data[j].date*1000, data[i].data[j].value]
                  }
                  series.push({
                    name: data[i].label,
                    data: data[i].data
                  })
                }
                function getLangOptions(culture) {
                  const formatDate = (date, options) => (new Intl.DateTimeFormat(culture, options)).format(date);
                  const formattedNumber = (new Intl.NumberFormat(culture)).formatToParts(99999.99);
                    const { value: decimalPoint } =
                      formattedNumber.find((part) => part.type === 'decimal');
                    const { value: thousandsSep } =
                      formattedNumber.find((part) => part.type === 'group');
                    const daysOfWeek = new Array(7)
                      .fill(0)
                      .map((_, i) => {
                        const date = new Date(2021, 1, i + 1);
                        return {
                          day: date.getDay(),
                          weekday: formatDate(date, { weekday: 'long' }),
                          shortWeekday: formatDate(date, { weekday: 'short' }),
                        };
                      })
                      .sort((a, b) => a.day - b.day);
                    const months = new Array(12)
                      .fill(0)
                      .map((_, i) => {
                        const date = new Date(2021, i + 1);
                        return {
                          month: date.getMonth(),
                          shortMonth: formatDate(date, { month: 'short' }),
                          longMonth: formatDate(date, { month: 'long' }),
                        };
                      })
                      .sort((a, b) => a.month - b.month);
                    return {
                      decimalPoint: decimalPoint,
                      thousandsSep: thousandsSep,
                      weekdays: daysOfWeek.map((d) => d.weekday),
                      shortWeekdays: daysOfWeek.map((d) => d.shortWeekday),
                      months: months.map((d) => d.longMonth),
                      shortMonths: months.map((d) => d.shortMonth),
                    };
                }
                Highcharts.setOptions({
                  lang: getLangOptions('de-de')
                })
                var config = {
                  time: {useUTC: false},
                  accessibility: {enabled: false},
                  colors: ['#99c', '#f90', '#c69', '#3c9', '#24CBE5', '#64E572',
                 '#FF9655', '#FFF263', '#6AF9C4'],
                  chart: {type: 'spline', backgroundColor: {color: '#000'}},
                  title: {text: ''}, subtitle: {text: ''},
                  xAxis: {type: 'datetime', gridLineColor:'#fc9', lineColor: '#fc9',minorTickColor: '#fc9', tickColor: '#fc9', labels: {style: {color: '#fc9'}}},
                  yAxis: {title: {text: ''}, gridLineColor:'#fc9', labels: {style: {color: '#fc9'}}},
                  legend: {itemStyle: {color: '#fc9'}},
                  tooltip: {borderColor: '#99c', backgroundColor: '#000',style: {color: '#fc9'}, valueDecimals:data[0].decimal}, 
                  series: series,
                  plotOptions: {
                    series: {
                      lineWidth: 3,
                      marker: {
                        enabled: false
                      }
                    }
                  },
                  backgroundColor: null
                }
                if (_options.style == 'line_stack') {
                  config.plotOptions.series['stacking'] = 'normal'
                }
                Highcharts.chart(_id+'_content', config)
              })
            }
          })
        }
      })
    })(jQuery)
    return $.lcWindowChart
  })