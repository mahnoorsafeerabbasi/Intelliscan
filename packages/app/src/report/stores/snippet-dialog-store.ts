import { useStore } from "zustand";
import { createStore } from "zustand/vanilla";
import { DialogStoreState, initialDialogState } from "./dialog-store-utils";

export const SnippetDialogStore = createStore<DialogStoreState>((set) => ({
  ...initialDialogState(set),
}));

export const useSnippetDialogStore = () => useStore(SnippetDialogStore);
