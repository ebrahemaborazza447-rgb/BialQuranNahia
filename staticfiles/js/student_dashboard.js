// static/js/student_dashboard.js

// Initialize weekly progress chart
function initWeeklyChart() {
    const chartDom = document.getElementById('weeklyChart');
    if (!chartDom) return;

    const chart = echarts.init(chartDom);
    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        grid: {
            right: '3%',
            left: '3%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: JSON.parse(document.getElementById('days-data').textContent || '[]'),
            axisLine: { lineStyle: { color: '#9ca3af' } },
            axisLabel: { color: '#6b7280' }
        },
        yAxis: {
            type: 'value',
            axisLine: { show: false },
            axisLabel: { color: '#6b7280' },
            splitLine: { lineStyle: { color: '#e5e7eb' } }
        },
        series: [{
            data: JSON.parse(document.getElementById('values-data').textContent || '[]'),
            type: 'bar',
            showBackground: true,
            backgroundStyle: { color: 'rgba(180, 180, 180, 0.1)' },
            itemStyle: {
                color: '#2563eb',
                borderRadius: [4, 4, 0, 0]
            }
        }]
    };

    chart.setOption(option);
    window.addEventListener('resize', chart.resize);
}

// Initialize progress rings
function initProgressRings() {
    const rings = document.querySelectorAll('.progress-ring-circle');
    rings.forEach(ring => {
        const circle = ring;
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        const percent = parseInt(circle.getAttribute('data-percent') || '0', 10);
        const offset = circumference - (percent / 100) * circumference;
        
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = circumference;
        circle.style.strokeDashoffset = offset;
    });
}

// Add hover effects to cards
function initCardHoverEffects() {
    const cards = document.querySelectorAll('.card-hover');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
        });
    });
}

// Initialize tab functionality
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            tabButtons.forEach(btn => 
                btn.classList.remove('active', 'bg-primary', 'text-white')
            );
            this.classList.add('active', 'bg-primary', 'text-white');
        });
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (typeof echarts !== 'undefined') {
        initWeeklyChart();
    }
    initProgressRings();
    initCardHoverEffects();
    initTabs();
});
