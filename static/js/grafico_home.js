// Espera a que la página se cargue completamente (buena práctica)
document.addEventListener('DOMContentLoaded', (event) => {
  
  // 1. Localiza el 'div' del gráfico
  const chartDom = document.getElementById('chart_home');
  // 2. Inicializa la librería ECharts en ese div
  const myChart = echarts.init(chartDom);
  let option;

  // 3. Define la configuración del NUEVO gráfico
  option = {
    // Información al pasar el mouse
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow' // Sombra sobre la barra
      }
    },

    // Caja de herramientas (la mantenemos, es útil)
    toolbox: {
      feature: {
        dataView: { show: true, readOnly: false, title: 'Ver Datos' },
        magicType: { show: true, type: ['line', 'bar'], title: { line: 'Línea', bar: 'Barras' } },
        restore: { show: true, title: 'Restaurar' },
        saveAsImage: { show: true, title: 'Guardar' }
      },
      iconStyle: {
        borderColor: '#fff' // Íconos en blanco
      }
    },

    // Ajuste de márgenes
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },

    // Eje X (Categorías)
    xAxis: {
      type: 'category',
      // USA LOS DATOS DE DJANGO
      data: window.graficoLabels || ['(Sin Datos)'], // Usa los datos o un marcador de posición
      axisLabel: {
        color: '#fff' // Texto en blanco
      }
    },

    // Eje Y (Valores)
    yAxis: {
      type: 'value',
      name: 'Total de Partos',
      nameTextStyle: {
        color: "#fff",
        fontWeight: "bold"
      },
      axisLabel: {
        color: '#fff' // Texto en blanco
      }
    },

    // Definición de la Serie de Datos
    series: [
      {
        name: 'Total de Partos',
        type: 'bar', // Tipo barra
        barWidth: '60%',
        // USA LOS DATOS DE DJANGO
        data: window.graficoData || [0], // Usa los datos o un marcador de posición
        // Estilo visual
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  };

  // 4. Aplica la configuración al gráfico
  option && myChart.setOption(option);

  // 5. Hace que el gráfico se redibuje si cambia el tamaño de la ventana
  window.addEventListener('resize', function() {
    myChart.resize();
  });
});