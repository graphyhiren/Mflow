import React from 'react';
import { IntlProvider } from 'react-intl';
import './index.css';
import '@databricks/design-system/dist/index.css';
import '@databricks/design-system/dist/index-dark.css';
import App from './experiment-tracking/components/App';
import { Provider } from 'react-redux';
import store from './store';
import { useI18nInit } from './i18n/I18nUtils';
import { DesignSystemContainer } from './common/components/DesignSystemContainer';
import { ConfigProvider } from 'antd';
import { LegacySkeleton } from '@databricks/design-system';
import { shouldUsePathRouting } from './common/utils/FeatureUtils';
import { MlflowRouter } from './MlflowRouter';

export function MLFlowRoot() {
  const i18n = useI18nInit();
  const [isDarkTheme, setIsDarkTheme] = React.useState(false);

  if (!i18n) {
    return (
      <DesignSystemContainer>
        <LegacySkeleton />
      </DesignSystemContainer>
    );
  }

  const { locale, messages } = i18n;

  return (
    <IntlProvider locale={locale} messages={messages}>
      <Provider store={store}>
        <DesignSystemContainer isDarkTheme={isDarkTheme}>
          <ConfigProvider prefixCls='ant'>
            {shouldUsePathRouting() ? (
              <MlflowRouter />
            ) : (
              <App isDarkTheme={isDarkTheme} setIsDarkTheme={setIsDarkTheme} />
            )}
          </ConfigProvider>
        </DesignSystemContainer>
      </Provider>
    </IntlProvider>
  );
}
