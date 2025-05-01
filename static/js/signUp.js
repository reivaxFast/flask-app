const canvas = document.getElementById('background');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
ctx.fillStyle = '#fff';
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = '#E1E1FF';
ctx.lineWidth = 30;
ctx.fillStyle = '#999';
for (let i = 2; i < 8; i++) {
    ctx.save();
    ctx.translate((canvas.width / 2), (canvas.height / 2));
    ctx.rotate(0.2 * i);
    ctx.strokeRect(-(15*i*i), -(15 * i*i),30*i*i, 30*i*i);
    ctx.restore();
}
function signUp() {
    location.href = "otp.html";
}

const password1 = document.getElementById('password1');
const password2 = document.getElementById('password2');
const togglePassword1 = document.getElementById('eye-password1');
const togglePassword2 = document.getElementById('eye-password2');
togglePassword1.addEventListener('click', function () {
    const type = password1.getAttribute('type') === 'password' ? 'text' : 'password';
    password1.setAttribute('type', type);
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
});
togglePassword2.addEventListener('click', function () {
    const type = password2.getAttribute('type') === 'password' ? 'text' : 'password';
    password2.setAttribute('type', type);
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
});