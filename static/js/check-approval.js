function checkApproval() {
    fetch('/check-approval/')
        .then(response => response.json())
        .then(data => {
            if (data.approved) {
                // عرض رابط "صفحتي"
                document.getElementById('myPageLink').style.display = 'inline-block';
            }
        });
}

// فحص كل 30 ثانية
setInterval(checkApproval, 30000);

// كمان نفحص أول ما الصفحة تفتح
checkApproval();
