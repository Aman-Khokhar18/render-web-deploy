document.addEventListener('DOMContentLoaded', () => {
  /* ======================================================
     1. HERO PARTICLES (tsParticles)
  ======================================================= */
  tsParticles.load("ml-particles", {
    fullScreen: { enable: false },
    fpsLimit: 60,
    background: { color: "transparent" },
    particles: {
      number: { value: 50, density: { enable: true, value_area: 800 } },
      color: { value: "#ff4d4d" }, /* Bright Red */
      shape: { type: "circle" },
      opacity: { value: 0.5 },
      size: { value: 3, random: true },
      links: { /* Updated from line_linked to links as per newer tsParticles */
        enable: true,
        distance: 130,
        color: "#cc0000", /* Darker Red */
        opacity: 0.4,
        width: 1
      },
      move: {
        enable: true,
        speed: 1.5,
        direction: "none",
        random: false,
        straight: false,
        outModes: { default: "out" } /* Updated for tsParticles v2 */
      }
    },
    interactivity: {
      detectsOn: "canvas",
      events: {
        onHover: { enable: true, mode: "repulse" },
        onClick: { enable: true, mode: "push" }
      },
      modes: {
        repulse: { distance: 100, duration: 0.4 },
        push: { quantity: 4 }
      }
    },
    detectRetina: true
  });

  /* ======================================================
     2. TIMELINE PARTICLES (tsParticles)
  ======================================================= */
  tsParticles.load("timeline-particles", {
    fullScreen: { enable: false },
    fpsLimit: 60,
    background: { color: "transparent" },
    particles: {
      number: { value: 30, density: { enable: true, value_area: 600 } },
      color: { value: "#ff4d4d" }, /* Bright Red */
      shape: { type: "circle" },
      opacity: { value: 0.3 },
      size: { value: 2, random: true },
      links: { /* Updated from line_linked to links as per newer tsParticles */
        enable: true,
        distance: 100,
        color: "#cc0000", /* Darker Red */
        opacity: 0.2,
        width: 1
      },
      move: {
        enable: true,
        speed: 1,
        direction: "none",
        outModes: { default: "out" } /* Updated for tsParticles v2 */
      }
    },
    interactivity: {
      detectsOn: "canvas",
      events: {
        onHover: { enable: true, mode: "repulse" },
        onClick: { enable: true, mode: "push" }
      },
      modes: {
        repulse: { distance: 80, duration: 0.4 },
        push: { quantity: 2 }
      }
    },
    detectRetina: true
  });

  /* =================================================
     3. FADE-IN TIMELINE BRANCHES
  ==================================================== */
  const branches = document.querySelectorAll('.branch');
  const branchObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
      } else {
        // Remove if you want them to fade out upon leaving
        entry.target.classList.remove('show');
      }
    });
  }, { threshold: 0.1 });

  branches.forEach(branch => branchObserver.observe(branch));

  /* ======================================================
     4. REMOVE HIGHLIGHT NAV LINKS ON SCROLL
  ======================================================= */
  /* The following code was responsible for adding the 'active' class
     to navigation links based on scroll position. Since we no longer
     want to highlight the current section in the navbar, we remove this functionality.
  */

  /* ======================================================
     5. SMOOTH SCROLL FOR NAVIGATION LINKS
  ======================================================= */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const targetID = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetID);

      if (targetElement) {
        const navHeight = document.querySelector('.navbar').offsetHeight;
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - navHeight - 10; // Additional offset

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  /* =================================================
     6. FADE-IN FOR PROJECT CARDS
  ==================================================== */
  const projectCards = document.querySelectorAll('.project-card');
  const projectObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
      } else {
        entry.target.classList.remove('show');
      }
    });
  }, { threshold: 0.1 });

  projectCards.forEach(card => projectObserver.observe(card));

  /* =================================================
     7. FADE-IN FOR SKILLS
  ==================================================== */
  const skillElements = document.querySelectorAll('.skill');
  const skillObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
      } else {
        entry.target.classList.remove('show');
      }
    });
  }, { threshold: 0.1 });

  skillElements.forEach(skill => skillObserver.observe(skill));

 /* ======================================================
     8. CHATBOT LOGIC
  ======================================================= */
  const chatInput = document.getElementById('chat-input');
  const chatSend = document.getElementById('chat-send');
  const chatOutput = document.getElementById('chat-output');
  const chatIcon = document.getElementById('chat-icon');
  const chatModal = document.getElementById('chat-modal');
  const chatClose = document.getElementById('chat-close');

  let isChatOpen = false; // Track chat modal state

  if (chatModal) {
    chatModal.style.display = 'none';
    chatModal.setAttribute('aria-hidden', 'true');
  }

  // Function to open the chatbot modal
  function openChatModal() {
    chatModal.style.display = 'flex';
    chatModal.setAttribute('aria-hidden', 'false');
    chatInput.focus(); // Focus on input when modal opens
    isChatOpen = true;

    // Auto-scroll to the bottom when modal opens
    scrollToBottom();
  }

  // Function to close the chatbot modal
  function closeChatModal() {
    chatModal.style.display = 'none';
    chatModal.setAttribute('aria-hidden', 'true');
    isChatOpen = false;
  }

  // Function to toggle chatbot modal
  function toggleChatModal(event) {
    // Prevent auto-opening on page load
    if (event && event.type === "DOMContentLoaded") {
      return;
    }

    if (!chatModal) return;

    if (isChatOpen) {
      closeChatModal();
    } else {
      openChatModal();
    }
  }

  // Event listener for chat icon click (toggle)
  if (chatIcon) {
    chatIcon.addEventListener('click', toggleChatModal);
    // Allow keyboard accessibility (Enter and Space)
    chatIcon.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        toggleChatModal();
      }
    });
  }

  // Event listener for close button click
  if (chatClose) {
    chatClose.addEventListener('click', closeChatModal);
  }

  // Event listener for clicks outside the modal content to close the modal
  window.addEventListener('click', (event) => {
    if (event.target === chatModal) {
      closeChatModal();
    }
  });

  // Event listener for 'Escape' key to close the modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isChatOpen) {
      closeChatModal();
    }
  });

  if (chatInput && chatSend && chatOutput) {
    // On "Send" button click
    chatSend.addEventListener('click', async () => {
      await sendMessage();
    });

    // On Enter key press in the input field
    chatInput.addEventListener('keypress', async (e) => {
      if (e.key === 'Enter') {
        e.preventDefault(); // Prevent form submission or default behavior
        await sendMessage();
      }
    });
  }

  // Function to send a message
  async function sendMessage() {
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    // Display user message
    appendMessage('user', `You: ${userMessage}`);
    // Clear input
    chatInput.value = '';

    // Display spinner as bot is typing
    const spinnerMessage = document.createElement('div');
    spinnerMessage.classList.add('message', 'bot');
    spinnerMessage.innerHTML = `<span class="spinner"></span> Bot is typing...`;
    chatOutput.appendChild(spinnerMessage);
    scrollToBottom();

    // Call your backend /chat endpoint
    try {
      const response = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });
     
      const data = await response.json();
      // Remove spinner
      chatOutput.removeChild(spinnerMessage);
      
      if (data.reply) {
        appendMessage('bot', `Bot: ${data.reply}`);
      } else {
        appendMessage('bot', 'Bot: [No response]');
      }
    } catch (err) {
      console.error(err);
      // Remove spinner
      chatOutput.removeChild(spinnerMessage);
      appendMessage('bot', 'Bot: [Error connecting to chatbot]');
    }

    // Auto-scroll to the bottom after bot response
    scrollToBottom();
  }

  
  // Function to append a message to the chat box
  function appendMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.textContent = text;
    chatOutput.appendChild(messageDiv);
    scrollToBottom(); // Auto-scroll after appending message
  }

  // Function to scroll the chat box to the bottom
  function scrollToBottom() {
    chatOutput.scrollTo({
      top: chatOutput.scrollHeight,
      behavior: 'smooth' // Smooth scroll
    });
  }



/* =================================================
   9. FADE-IN FOR CERTIFICATIONS
==================================================== */
const certificationCards = document.querySelectorAll('.certification-card');
const certificationObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('show');
    } else {
      entry.target.classList.remove('show');
    }
  });
}, { threshold: 0.1 });


certificationCards.forEach(card => certificationObserver.observe(card));

 /* ======================================================
     10. IMAGE CAROUSEL FUNCTIONALITY
  ======================================================= */
  const carousels = document.querySelectorAll(".project-carousel");

  carousels.forEach((carousel) => {
    const slideContainer = carousel.querySelector(".carousel-slide");
    const slides = slideContainer.children;
    const prevButton = carousel.querySelector(".prev");
    const nextButton = carousel.querySelector(".next");

    let index = 0;

    function updateCarousel() {
      const slideWidth = slides[0].clientWidth; // Get the width of a single slide
      slideContainer.style.transform = `translateX(-${index * slideWidth}px)`;
    }

    nextButton.addEventListener("click", function () {
      if (index < slides.length - 1) {
        index++;
      } else {
        index = 0; // Loop back to first slide
      }
      updateCarousel();
    });

    prevButton.addEventListener("click", function () {
      if (index > 0) {
        index--;
      } else {
        index = slides.length - 1; // Loop to last slide
      }
      updateCarousel();
    });

    updateCarousel();

    // Ensure correct width on resize
    window.addEventListener("resize", updateCarousel);
  });
});