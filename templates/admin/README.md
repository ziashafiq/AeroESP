# Admin templates

`base_site.html.pre-unfold` is the pre-Unfold admin skin, kept for
reference and rollback. It is **inert**: Django resolves the admin's
base template by the exact name `admin/base_site.html`, so the
`.pre-unfold` suffix takes it out of the lookup path.

It styled the stock Django admin via
`static/admin/css/aeroesp_admin.css`, which targeted selectors
(`#header`, `.module`, `#content`) that Unfold's Tailwind markup does
not have. That CSS file is likewise still in the repo and likewise no
longer linked from anywhere.

The branding it used to provide - site title, logo, "View site" target -
now comes from the `UNFOLD` dict in `config/settings.py`.

To roll back to the old skin: remove `unfold*` from `INSTALLED_APPS`,
drop the `UNFOLD` setting, rename this file back to `base_site.html`,
and revert the `unfold.admin.ModelAdmin` imports in the six apps'
`admin.py`.
