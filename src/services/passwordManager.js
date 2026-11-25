export function offerPasswordSave(identifier, password) {
  if (
    !window.isSecureContext ||
    typeof window.PasswordCredential !== 'function' ||
    !navigator.credentials?.store
  ) {
    return
  }

  try {
    const credential = new window.PasswordCredential({ id: identifier, password })
    navigator.credentials.store(credential).catch(error => {
      console.warn('The browser password manager did not save the Hali sign-in.', error)
    })
  } catch (error) {
    console.warn('The browser password manager did not save the Hali sign-in.', error)
  }
}
