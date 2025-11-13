window.tailwind = {
  config: {
    theme: {
      extend: {
        colors: {
          'blue-400': '#60a5fa',
          'blue-500': '#3b82f6',
          'purple-500': '#a855f7'
        }
      }
    }
  }
};
// 간단한 인터섹션 애니메이션
document.addEventListener('DOMContentLoaded', function() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  document.querySelectorAll('.fade-in, .fade-in-delay, .fade-in-delay-2').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.8s ease-out, transform 0.8s ease-out';
    observer.observe(el);
  });
});

