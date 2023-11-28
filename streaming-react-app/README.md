# 🚀 Streaming React App

## Getting Started

- `yarn run dev` - Run the app with a development server that supports hot module reloading

## URL Parameters

You can provide URL parameters in order to change the behavior of the app. Those are documented in [URLParams.ts](src/URLParams.ts).

# Vite Information: React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
   parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    project: ['./tsconfig.json', './tsconfig.node.json'],
    tsconfigRootDir: __dirname,
   },
```

- Replace `plugin:@typescript-eslint/recommended` to `plugin:@typescript-eslint/recommended-type-checked` or `plugin:@typescript-eslint/strict-type-checked`
- Optionally add `plugin:@typescript-eslint/stylistic-type-checked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and add `plugin:react/recommended` & `plugin:react/jsx-runtime` to the `extends` list

# To Deploy to AWS

1. Acquire AWS credentials (not needed if already on an EC2 instance with permissions)

On your local mac use the following command.

```
eval $(corp_cloud aws get-creds 790537050551)
```

2. Deploy to AWS

Build the react and copy the contents of [dist](dist) folder to s3 bucket and then invalidate the cloudfront (CDN) cache. Note step 2 has been automated using `yarn deploy_dev`

To deploy to the (old) seamless-vc s3 bucket:

```
yarn build:dev_vc
yarn deploy_dev_vc
```

To deploy to the (new) seamless-vr terraform-based s3 bucket:

```
yarn build:dev_vr
yarn deploy_dev_vr
```
