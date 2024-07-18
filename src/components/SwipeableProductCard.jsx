import React from 'react';
import { useSwipeable } from 'react-swipeable';
import './SwipeableProductCard.css';

const SwipeableProductCard = ({ product, onSwipeLeft, onSwipeRight }) => {
  const handlers = useSwipeable({
    onSwipedLeft: () => onSwipeLeft(product),
    onSwipedRight: () => onSwipeRight(product),
    preventDefaultTouchmoveEvent: false,
    trackMouse: true,
  });

  return (
    <div {...handlers} className="product-card">
      <div className="product-image-container">
        <img
          className="product-image"
          src={product.productImage}
          alt={product.productName}
        />
      </div>
      <div className="product-info">
        <h2>
          {product.productName} <span className="product-rating">4.3⭐</span>
        </h2>
        <p>{product.productDescription}</p>
        <p className="product-price">${product.productPrice}</p>
      </div>
      <div className="product-actions">
        <button className="action-btn undo">↺</button>
        <button className="action-btn dislike">✖</button>
        <button className="action-btn cart">🛒</button>
        <button className="action-btn like">❤</button>
        <button className="action-btn save">🔖</button>
      </div>
    </div>
  );
};

export default SwipeableProductCard;
