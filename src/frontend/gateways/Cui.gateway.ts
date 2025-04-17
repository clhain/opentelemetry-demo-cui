// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { useRouter } from 'next/router';
import { CUINames } from '../utils/enums/Cui';


const {
  NEXT_PUBLIC_PRODUCT_NAME = 'DEMO_SHOP',
} = typeof window !== 'undefined' ? window.ENV : {};
const defaultCui = `${NEXT_PUBLIC_PRODUCT_NAME}/${CUINames.UNKNOWN}`


/**
 * Guess at a CUI based on the broser path and /or API Call being made.
 */
const guessCui = (path: string, apiName: string) => {
  // Process CUIs that map directly to a specific API Call
  switch (apiName) {
    case "addCartItem": {
      return `${NEXT_PUBLIC_PRODUCT_NAME}.${CUINames.ADD_TO_CART}`
    }
    case "emptyCart": {
      return `${NEXT_PUBLIC_PRODUCT_NAME}.${CUINames.EMPTY_CART}`
    }
    case "placeOrder": {
      return `${NEXT_PUBLIC_PRODUCT_NAME}.${CUINames.CHECKOUT}`
    }
    default: {
      break
    }
  }
  // Process CUIs by exact url path
  switch (path) {
    case "/": {
      return `${NEXT_PUBLIC_PRODUCT_NAME}.${CUINames.BROWSE}` 
    }
    case "/cart": {
      return `${NEXT_PUBLIC_PRODUCT_NAME}.${CUINames.VIEW_CART}` 
    }
    default: {
      break
    }
  }

  // Process CUIs with dynamic url paths
  if(path.startsWith('/cart/checkout/')){
    return `${NEXT_PUBLIC_PRODUCT_NAME}.${CUINames.VIEW_ORDER}` 
  }
  // Process CUIs with dynamic url paths
  if(path.startsWith('/cart/checkout/')){
    return `${NEXT_PUBLIC_PRODUCT_NAME}.${CUINames.VIEW_ORDER}` 
  }
  if(path.startsWith('/product/')){
    return `${NEXT_PUBLIC_PRODUCT_NAME}.${CUINames.VIEW_ITEM}` 
  }
  
  return `${NEXT_PUBLIC_PRODUCT_NAME}.${CUINames.UNKNOWN}` 
}


const CUIGateway = () => ({
  getCUI(apiName: string): string {
    if (typeof window === 'undefined') return defaultCui;
    const path = window.location.pathname
    return guessCui(path, apiName)
  }
});

export default CUIGateway();
