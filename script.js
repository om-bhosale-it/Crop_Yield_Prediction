document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Mouse Parallax Effect on Background Image
    const bgImage = document.querySelector(".bg-image");
    
    if (bgImage) {
        document.addEventListener("mousemove", (e) => {
            const x = (window.innerWidth / 2 - e.clientX) / 40;
            const y = (window.innerHeight / 2 - e.clientY) / 40;
            bgImage.style.transform = `scale(1.05) translate(${x}px, ${y}px)`;
        });
    }

    // 2. 3D Tilt Effect on Cards
    const cards = document.querySelectorAll(".tilt-card");
    
    cards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 12;
            const rotateY = (centerX - x) / 12;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)";
        });
    });

    // 3. Form Validation with Glow Notification
    const form = document.querySelector(".glass-form");
    if (form) {
        form.addEventListener("submit", function (e) {
            const inputs = form.querySelectorAll("input, select");
            let isValid = true;

            inputs.forEach(input => {
                if (input.value.trim() === "") {
                    isValid = false;
                    input.style.borderColor = "#ef4444";
                    input.style.boxShadow = "0 0 15px rgba(239, 68, 68, 0.4)";
                } else {
                    input.style.borderColor = "rgba(255, 255, 255, 0.15)";
                    input.style.boxShadow = "none";
                }
            });

            if (!isValid) {
                e.preventDefault();
                showToast("⚠️ कृपया सर्व माहिती अचूक भरा!");
            }
        });
    }
});

// Toast Alert System
function showToast(message) {
    let toast = document.getElementById("custom-toast");
    
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "custom-toast";
        
        Object.assign(toast.style, {
            position: "fixed",
            bottom: "30px",
            right: "30px",
            background: "rgba(21, 128, 61, 0.95)",
            backdropFilter: "blur(15px)",
            color: "#ffffff",
            padding: "16px 30px",
            borderRadius: "50px",
            boxShadow: "0 10px 30px rgba(0,0,0,0.6)",
            fontSize: "15px",
            fontWeight: "700",
            zIndex: "9999",
            opacity: "0",
            transform: "translateY(20px)",
            transition: "all 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
            border: "1px solid rgba(255,255,255,0.2)"
        });

        document.body.appendChild(toast);
    }

    toast.innerText = message;
    
    setTimeout(() => {
        toast.style.opacity = "1";
        toast.style.transform = "translateY(0)";
    }, 100);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(20px)";
    }, 3500);
}