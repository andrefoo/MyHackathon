import React, { useEffect, useRef, useState } from 'react';
import './Home.css';
import VideoCard from './components/VideoCard';
import BottomNavbar from './components/BottomNavbar';
import TopNavbar from './components/TopNavbar';
import SwipeableProductCard from './components/SwipeableProductCard';
import { items } from './data';
import { initialProducts } from './products'; // Importing products

const Home = () => {
  const videoRefs = useRef([]);
  const [products, setProducts] = useState(initialProducts);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [toastMessage, setToastMessage] = useState('');

  useEffect(() => {
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.8,
    };

    const handleIntersection = (entries) => {
      entries.forEach((entry) => {
        const videoElement = entry.target;
        if (entry.isIntersecting) {
          videoElement.play();
        } else {
          videoElement.pause();
        }
      });
    };

    const observer = new IntersectionObserver(handleIntersection, observerOptions);

    const handleUserInteraction = () => {
      videoRefs.current.forEach((videoRef) => {
        if (videoRef) {
          observer.observe(videoRef);
        }
      });
      window.removeEventListener('click', handleUserInteraction);
      window.removeEventListener('touchstart', handleUserInteraction);
    };

    window.addEventListener('click', handleUserInteraction);
    window.addEventListener('touchstart', handleUserInteraction);

    return () => {
      observer.disconnect();
      window.removeEventListener('click', handleUserInteraction);
      window.removeEventListener('touchstart', handleUserInteraction);
    };
  }, []);

  const handleVideoRef = (index) => (ref) => {
    videoRefs.current[index] = ref;
  };

  const handleSwipeLeft = (product) => {
    setToastMessage(`Removed ${product.productName}`);
    setTimeout(() => setToastMessage(''), 3000);
    setProducts((prevProducts) => prevProducts.filter((p) => p !== product));
  };

  const handleSwipeRight = (product) => {
    setToastMessage(`Liked ${product.productName}`);
    setTimeout(() => setToastMessage(''), 3000);
    setProducts((prevProducts) => prevProducts.filter((p) => p !== product));
  };

  return (
    <div className="app">
      <div className="container">
        <TopNavbar />
        {items.map((item, index) => {
          if (item.type === 'video') {
            return (
              <VideoCard
                key={index}
                username={item.username}
                description={item.description}
                song={item.song}
                likes={item.likes}
                saves={item.saves}
                comments={item.comments}
                shares={item.shares}
                url={item.url}
                profilePic={item.profilePic}
                setVideoRef={handleVideoRef(index)}
                autoplay={index === 0}
              />
            );
          } else if (item.type === 'product' && products.length > 0) {
            return (
              <div className="home-container" key={index}>
                {products.map((product, idx) => (
                  <div
                    key={product.productName}
                    className={`swipeable-card-container ${idx === currentIndex ? 'active' : ''}`}
                  >
                    <SwipeableProductCard
                      product={product}
                      onSwipeLeft={handleSwipeLeft}
                      onSwipeRight={handleSwipeRight}
                    />
                  </div>
                ))}
              </div>
            );
          }
          return null;
        })}
        <BottomNavbar />
        {toastMessage && <div className="toast">{toastMessage}</div>}
      </div>
    </div>
  );
};

export default Home;
