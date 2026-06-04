const API_URL = window.location.origin;

window.addEventListener('load', () => {
  document.getElementById('preloader').classList.add('hidden');
  setTimeout(() => { document.getElementById('preloader').style.display = 'none'; }, 600);
});

window.addEventListener('scroll', () => {
  document.getElementById('mainNav').classList.toggle('scrolled', window.scrollY > 50);
});

AOS.init({ duration: 800, once: true });

fetch(`${API_URL}/api/courses`)
  .then(res => res.json())
  .then(courses => {
    const container = document.getElementById('coursesContainer');
    container.innerHTML = courses.map(c => `
      <div class="col-lg-4 col-md-6" data-aos="fade-up">
        <div class="course-card h-100">
          <img src="${c.image_url}" class="course-img" alt="${c.name}">
          <div class="course-body">
            <h5>${c.name}</h5>
            <p><i class="fa-regular fa-clock gold-text"></i> ${c.duration || 'Short Course'}</p>
            <div class="d-flex justify-content-between align-items-center">
              <span class="course-fee">Rs. ${c.full_payment.toLocaleString()}</span>
              ${c.monthly_fee ? `<small class="text-muted">Monthly: ${c.monthly_fee}/-</small>` : ''}
            </div>
            ${c.admission_fee ? `<small class="text-muted">Admission: ${c.admission_fee}/-</small>` : ''}
          </div>
        </div>
      </div>
    `).join('');
  });

document.getElementById('signupForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = document.getElementById('signupName').value;
  const email = document.getElementById('signupEmail').value;
  const password = document.getElementById('signupPassword').value;
  const res = await fetch(`${API_URL}/api/signup`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name, email, password})
  });
  const data = await res.json();
  if (res.ok) {
    alert('Signup successful! You are logged in.');
    bootstrap.Modal.getInstance('#signupModal').hide();
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  } else {
    alert(data.message || 'Signup failed');
  }
});

document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const res = await fetch(`${API_URL}/api/login`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, password})
  });
  const data = await res.json();
  if (res.ok) {
    alert('Login successful!');
    bootstrap.Modal.getInstance('#loginModal').hide();
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  } else {
    alert(data.message || 'Login failed');
  }
});

document.getElementById('adminLoginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('adminEmail').value;
  const password = document.getElementById('adminPassword').value;
  const res = await fetch(`${API_URL}/api/admin/login`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, password})
  });
  const data = await res.json();
  if (res.ok) {
    alert('Admin login successful!');
    bootstrap.Modal.getInstance('#adminLoginModal').hide();
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  } else {
    alert(data.message || 'Admin login failed');
  }
});
