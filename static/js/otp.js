const canvas = document.getElementById('background');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
ctx.strokeStyle = '#E1E1FF';
ctx.fillStyle = '#E1E1FF';
ctx.lineWidth = 30;
for (let i = 0; i < 8; i++) {
    ctx.save();
    ctx.translate(canvas.width-300, canvas.height / 2);
    ctx.rotate(Math.PI * i / 4);
    ctx.strokeRect(50, 50, 400, 400);
    ctx.restore();
}
for (let i = 0; i < 6; i++) {
    ctx.beginPath();
    ctx.arc(0, 0, i*100, 0, Math.PI*2);
    ctx.stroke();
}
ctx.strokeRect(-15, canvas.height-285, 500, 300);
ctx.fillRect(-15, canvas.height-245, 460, 300);

const inputs = document.querySelectorAll('#otpContainer input');
inputs.forEach((input, index) => {
    input.addEventListener('input', () => {
        const value = input.value;
        if (value.length === 1 && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }
    });
    input.addEventListener('paste', (e) => {
        const pasteData = e.clipboardData.getData('text');
        if (pasteData.length === inputs.length && /^\d+$/.test(pasteData)) {
            e.preventDefault();
            pasteData.split('').forEach((char, i) => {
                inputs[i].value = char;
            });
            inputs[inputs.length - 1].focus();
        }
    });
});