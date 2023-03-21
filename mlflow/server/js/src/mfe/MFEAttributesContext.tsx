import React, { useContext } from 'react';

export interface MFECustomActionCallbacks {
  registerModel?: (...data: any[]) => void;
}

export interface MFEAttributesType {
  /**
   * Callbacks for custom overriden actions provided
   * externally when mounting application as a web component
   */
  customActionCallbacks?: MFECustomActionCallbacks;
  [k: string]: any;
}

const MFEAttributesContext = React.createContext<MFEAttributesType>({});

export const MFEAttributesContextProvider = ({
  value,
  children,
}: React.PropsWithChildren<{
  value: MFEAttributesType;
}>) => {
  return <MFEAttributesContext.Provider value={value}>{children}</MFEAttributesContext.Provider>;
};

/**
 * MFE attributes passed down from the overarching host application.
 */
export const useMFEAttributes = () => useContext(MFEAttributesContext) || ({} as MFEAttributesType);

/**
 * HoC allowing to use attributes context in class components
 */
export const withMFEAttributes =
  <P,>(Component: React.ComponentType<P>) =>
  (props: P) => {
    const appAttributes = useMFEAttributes();
    return <Component {...props} appAttributes={appAttributes} />;
  };
