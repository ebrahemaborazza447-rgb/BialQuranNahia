document.querySelectorAll('.phase-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            // إزالة التنشيط من جميع الأزرار
            document.querySelectorAll('.phase-btn').forEach(b => b.classList.remove('active'));
            // تفعيل الزر المحدد
            this.classList.add('active');

            // جلب المواعيد حسب المرحلة المختارة
            const phase = this.dataset.phase;
            fetch(`/ajax/get_appointments/?phase=${phase}`)
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('appointments-container');
                    container.innerHTML = '';
                    if (data.length === 0) {
                        container.innerHTML = '<p>لا توجد مواعيد متاحة حالياً. يرجى المحاولة لاحقاً.</p>';
                    } else {
                        data.forEach(appointment => {
                            const div = document.createElement('div');
                            div.className = 'appointment-time';
                            div.setAttribute('data-appointment-id', appointment.id);
                            div.setAttribute('data-trainer', appointment.trainer);
                            div.setAttribute('data-date', appointment.date);
                            div.setAttribute('data-time', appointment.time);
                            div.innerHTML = `${appointment.trainer} - ${appointment.date} ${appointment.time}`;
                            container.appendChild(div);
                        });

                        // إعادة تفعيل اختيار الموعد بعد تحديث القائمة
                        document.querySelectorAll('.appointment-time').forEach(item => {
                            item.addEventListener('click', function () {
                                document.querySelectorAll('.appointment-time').forEach(i => i.classList.remove('selected'));
                                this.classList.add('selected');
                                document.getElementById('appointment_id').value = this.dataset.appointmentId;
                            });
                        });
                    }
                });
        });
});