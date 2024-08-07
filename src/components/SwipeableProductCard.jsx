import React from 'react';
import PropTypes from 'prop-types';
import { useSwipeable } from 'react-swipeable';
import './SwipeableProductCard.css';
import iconsOng from './icons.ong.png'; // Adjust the path as needed

const SwipeableProductCard = ({ product, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown }) => {
  const handlers = useSwipeable({
    onSwipedLeft: () => onSwipeLeft(product),
    onSwipedRight: () => onSwipeRight(product),
    onSwipedUp: () => onSwipeUp(product),     // Add this line for swiping up
    onSwipedDown: () => onSwipeDown(product), // Add this line for swiping down
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
      <img className="product-actions" src={iconsOng} alt="Icon" />
    </div>
  );
};

SwipeableProductCard.propTypes = {
  product: PropTypes.shape({
    productName: PropTypes.string.isRequired,
    productDescription: PropTypes.string.isRequired,
    productPrice: PropTypes.number.isRequired,
    productImage: PropTypes.string.isRequired,
  }).isRequired,
  onSwipeLeft: PropTypes.func.isRequired,
  onSwipeRight: PropTypes.func.isRequired,
  onSwipeUp: PropTypes.func.isRequired,      // Add this line
  onSwipeDown: PropTypes.func.isRequired,    // Add this line
};

export default SwipeableProductCard;
