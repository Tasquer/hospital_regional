// static/js/dashboard_turno.js

document.addEventListener('DOMContentLoaded', () => {
  
  // Verificar que ECharts esté disponible
  if (typeof echarts === 'undefined') {
    console.error('ECharts no está cargado');
    return;
  }

  // Gráfico de Actividad del Turno (Últimas 24 horas por hora)
  const chartTurno = echarts.init(document.getElementById('chart_turno'), 'dark');
  
  const optionTurno = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
      borderColor: '#374151',
      textStyle: { color: '#f3f4f6' },
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6366f1'
        }
      },
      formatter: function(params) {
        const param = params[0];
        return `<div style="padding: 8px;">
          <div style="font-weight: bold; margin-bottom: 4px;">${param.name}</div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 10px; height: 10px; background: #6366f1; border-radius: 50%;"></span>
            <span>${param.value} parto(s)</span>
          </div>
        </div>`;
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dashboardData.turno.labels,
      axisLabel: {
        color: '#9ca3af',
        fontSize: 11,
        interval: 0,
        rotate: 45,
        formatter: function(value) {
          // Mostrar solo la hora
          return value.split(' ')[1] || value;
        }
      },
      axisLine: {
        lineStyle: { color: '#374151' }
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      name: 'Partos',
      nameTextStyle: {
        color: '#9ca3af',
        fontSize: 12,
        padding: [0, 0, 0, 10]
      },
      axisLabel: {
        color: '#9ca3af',
        fontSize: 11
      },
      splitLine: {
        lineStyle: {
          color: '#374151',
          type: 'dashed'
        }
      },
      minInterval: 1 // Solo números enteros
    },
    series: [{
      name: 'Partos',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      data: dashboardData.turno.data,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(99, 102, 241, 0.5)' },
            { offset: 1, color: 'rgba(99, 102, 241, 0.05)' }
          ]
        }
      },
      lineStyle: {
        width: 3,
        color: '#6366f1',
        shadowColor: 'rgba(99, 102, 241, 0.5)',
        shadowBlur: 10,
        shadowOffsetY: 5
      },
      itemStyle: {
        color: '#6366f1',
        borderWidth: 2,
        borderColor: '#fff',
        shadowColor: 'rgba(99, 102, 241, 0.5)',
        shadowBlur: 5
      },
      emphasis: {
        focus: 'series',
        itemStyle: {
          color: '#818cf8',
          borderColor: '#fff',
          borderWidth: 3,
          shadowBlur: 10,
          shadowColor: 'rgba(99, 102, 241, 0.8)'
        }
      },
      // Marcar el último punto de forma especial
      markPoint: {
        symbol: 'pin',
        symbolSize: 50,
        data: [{
          type: 'max',
          name: 'Pico',
          itemStyle: {
            color: '#f59e0b'
          }
        }]
      },
      // Línea promedio
      markLine: {
        silent: true,
        lineStyle: {
          color: '#10b981',
          type: 'dashed',
          width: 2
        },
        label: {
          show: true,
          position: 'end',
          formatter: 'Promedio: {c}',
          color: '#10b981',
          fontSize: 11
        },
        data: [{
          type: 'average',
          name: 'Promedio'
        }]
      }
    }]
  };

  chartTurno.setOption(optionTurno);

  // Responsive
  window.addEventListener('resize', () => {
    chartTurno.resize();
  });

  // Auto-actualizar cada 5 minutos (opcional)
  // setInterval(() => {
  //   location.reload();
  // }, 300000);

});