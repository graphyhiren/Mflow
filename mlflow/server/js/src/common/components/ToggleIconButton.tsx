import type { ButtonProps } from '@databricks/design-system';
import { useDesignSystemTheme } from '@databricks/design-system';

export interface ToggleIconButtonProps extends ButtonProps {
  pressed?: boolean;
}

/**
 * WARNING: Temporary component!
 *
 * This component recreates "Toggle button with icon" pattern which is not
 * available in the design system yet.
 *
 * TODO: replace this component with the one from DuBois design system when available.
 */
export const ToggleIconButton = (props: ToggleIconButtonProps) => {
  const { pressed, onClick, icon } = props;
  const { theme } = useDesignSystemTheme();
  return (
    <button
      onClick={onClick}
      css={{
        cursor: 'pointer',
        width: theme.general.heightSm,
        height: theme.general.heightSm,
        borderRadius: theme.borders.borderRadiusMd,
        lineHeight: theme.typography.lineHeightBase,
        padding: 0,
        border: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: pressed ? theme.colors.actionDefaultBackgroundPress : 'transparent',
        color: pressed ? theme.colors.actionDefaultTextPress : theme.colors.textSecondary,
        '&:hover': {
          background: theme.colors.actionDefaultBackgroundHover,
          color: theme.colors.actionDefaultTextHover,
        },
      }}
    >
      {icon}
    </button>
  );
};
