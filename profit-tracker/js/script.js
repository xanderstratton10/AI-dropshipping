document.addEventListener('DOMContentLoaded', function() {
    // Navigation
    const navLinks = document.querySelectorAll('.sidebar nav a');
    const pages = document.querySelectorAll('.page');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Show target page
            pages.forEach(page => {
                if (page.id === targetId) {
                    page.style.display = 'block';
                } else {
                    page.style.display = 'none';
                }
            });
        });
    });

    // KPI Data and Dashboard Population
    const kpis = [
        { name: 'ROAS', current: 3.01, target: 2.5, unit: 'x' },
        { name: 'Conversion Rate', current: 2.8, target: 2.5, unit: '%' },
        { name: 'AOV', current: 48.50, target: 45.00, unit: '$' },
        { name: 'CAC', current: 16.12, target: 15.00, unit: '$' }
    ];

    const kpiBody = document.getElementById('kpi-body');
    kpis.forEach(kpi => {
        const isSuccess = kpi.name === 'CAC' ? kpi.current <= kpi.target : kpi.current >= kpi.target;
        const statusIcon = isSuccess ? '<i class="fas fa-check-circle status-check"></i>' : '<i class="fas fa-times-circle status-cross"></i>';
        
        const row = `
            <tr>
                <td>${kpi.name}</td>
                <td>${kpi.unit === '$' ? '$' + kpi.current.toFixed(2) : kpi.current + kpi.unit}</td>
                <td>${kpi.unit === '$' ? '$' + kpi.target.toFixed(2) : kpi.target + kpi.unit}</td>
                <td>${statusIcon}</td>
            </tr>
        `;
        kpiBody.innerHTML += row;
    });

    // Chart.js - Revenue vs Profit
    const ctx = document.getElementById('revenueChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [
                {
                    label: 'Revenue',
                    data: [3200, 4100, 3800, 4320],
                    backgroundColor: 'rgba(0, 188, 212, 0.6)',
                    borderColor: 'rgba(0, 188, 212, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Net Profit',
                    data: [1100, 1500, 1200, 1700],
                    backgroundColor: 'rgba(67, 160, 71, 0.6)',
                    borderColor: 'rgba(67, 160, 71, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) { return '$' + value; }
                    }
                }
            }
        }
    });

    // Profit Calculator Logic
    const calcBtn = document.getElementById('calculate-btn');
    calcBtn.addEventListener('click', function() {
        const revenue = parseFloat(document.getElementById('calc-rev').value) || 0;
        const units = parseInt(document.getElementById('calc-units').value) || 0;
        const unitCost = parseFloat(document.getElementById('calc-unit-cost').value) || 0;
        const adSpend = parseFloat(document.getElementById('calc-ad-spend').value) || 0;
        const shipping = parseFloat(document.getElementById('calc-shipping').value) || 0;
        const miscPercent = parseFloat(document.getElementById('calc-misc').value) || 0;

        // Calculations
        const totalCOGS = units * unitCost;
        const totalShipping = units * shipping;
        const miscFees = revenue * (miscPercent / 100);
        
        const grossProfit = revenue - totalCOGS;
        const netProfit = revenue - totalCOGS - adSpend - totalShipping - miscFees;
        const profitMargin = revenue > 0 ? (netProfit / revenue) * 100 : 0;
        const roas = adSpend > 0 ? revenue / adSpend : 0;

        // Break-even Analysis
        // Revenue per unit = revenue / units
        // Variable cost per unit = unitCost + shipping + (revPerUnit * misc%)
        // Contribution Margin = revPerUnit - varCostPerUnit
        // Break-even units = AdSpend / Contribution Margin
        const revPerUnit = units > 0 ? revenue / units : 0;
        const varCostPerUnit = unitCost + shipping + (revPerUnit * (miscPercent / 100));
        const contributionMargin = revPerUnit - varCostPerUnit;
        const breakEvenUnits = contributionMargin > 0 ? Math.ceil(adSpend / contributionMargin) : '∞';

        // Update UI
        document.getElementById('res-gross').textContent = '$' + grossProfit.toLocaleString(undefined, {minimumFractionDigits: 2});
        document.getElementById('res-net').textContent = '$' + netProfit.toLocaleString(undefined, {minimumFractionDigits: 2});
        document.getElementById('res-margin').textContent = profitMargin.toFixed(1) + '%';
        document.getElementById('res-roas').textContent = roas.toFixed(2) + 'x';
        document.getElementById('res-break-even').textContent = breakEvenUnits;

        // Style net profit based on value
        const netElem = document.getElementById('res-net');
        if (netProfit > 0) {
            netElem.style.color = '#43a047';
        } else if (netProfit < 0) {
            netElem.style.color = '#f44336';
        } else {
            netElem.style.color = 'inherit';
        }
    });

    // Trigger initial calculation
    calcBtn.click();
});
