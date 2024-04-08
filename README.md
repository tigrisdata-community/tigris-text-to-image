## Text To Image Generator with Hugging Face model, Fly GPUs and Tigris as storage 🤖📽️

A Text-To-Image Generator using huggingface [stable diffusion](https://github.com/runwayml/stable-diffusion) model 
to generate images. The app using Tigris as storage to save or load image. The app can be deployed
on fly to run the model on fly GPUs.

## Stack

- 💻 Image hosting: [Tigris](https://www.tigrisdata.com/)
- 🦙 Inference: [Huggingface](https://github.com/runwayml/stable-diffusion), 
- 🔌 GPU: [Fly](https://fly.io/)
- 🖌️ UI: [Gradio](https://www.gradio.app/)

## Overview

- 🚀 [Quickstart](#quickstart)
- 💻 [Useful Commands](#useful-commands)

## Quickstart

### Step 0: Fork this repo and clone it

```
git clone git@github.com:[YOUR_GITHUB_ACCOUNT_NAME]/tigris-text-to-image.git
```

### Step 1: Set up Tigris

1. Create an .env file

```
cd tigris-text-to-image
cp .env.example .env
```

2. Set up Tigris

- Make sure you have a fly.io account and have fly CLI installed on your computer
- `cd tigris-text-to-image`
- Pick a name for your version of your app. App names on fly are global, so it has to be unique. For example `tigris-text-to-image-awesomeness`
- Create the app on fly with `fly app create <your app name>` so for example `fly app create tigris-text-to-image-awesomeness`
- Create the storage with `fly storage create`
- You should get a list of credentials like below:
  <img width="859" alt="Screenshot 2024-03-24 at 5 40 36 PM" src="https://github.com/tigrisdata-community/multi-modal-starter-kit/assets/3489963/a400d444-8d5f-445e-a48a-1749f7595c47">
- If you get a list of keys without values, destroy the bucket with `fly storage destroy` and try again.
- Copy paste these values to your .env

3. Set Tigris bucket cors policy and bucket access policy

- `fly storage update YOUR_BUCKET_NAME --public`
- Make sure you have aws CLI installed and run `aws configure`. Enter the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` printed above. Note that these are not actual Amazon Web Services credentials, but Tigris credentials. If you have the aws CLI already configured for Amazon, it will overwrite those values.
- Run the following command to update CORS policy on the bucket
  ```
  aws s3api put-bucket-cors --bucket BUCKET_NAME --cors-configuration file://cors.json --endpoint-url https://fly.storage.tigris.dev/
  ```

### Step 2: Deploying on fly

By now you should have a functional app, let's deploy it to [fly.io](https://fly.io/) cloud account that you setup in Step 1.

- First, lets see what secrets are already available in our app using `fly secrets list`:

```bash
$ ➔  fly secrets list
NAME                            DIGEST         CREATED AT
AWS_ACCESS_KEY_ID               xxxxxxx        Feb 23 2024 20:33
AWS_ENDPOINT_URL_S3             xxxxxxx        Feb 23 2024 20:33
AWS_REGION                      xxxxxxx        Feb 23 2024 20:33
AWS_SECRET_ACCESS_KEY           xxxxxxx        Feb 23 2024 20:33
BUCKET_NAME                     xxxxxxx        Feb 23 2024 20:33
```

- We need to match the secrets as in `.env.example` file. 

- Now, all other environment vars:

- Once environment is all set, we can make the app fly:

```bash
$ ➔ fly launch
$ ➔ fly deploy
```

### Step 3: Try it out

The app allows you generate an image from the text and then it lets you save the image to Tigris. By default, it is
using the bucket in your .env file. You can also optionally store metadata about this image which Tigris will store
along the image. Try to save few images and then load one of the existing image stored.

## Local Development

If you want to tweak your app locally and run the generator then do the following:
  - Remove the suffix "+cu118" from torch package in requirements.go
  - Update the 'ARCH' environment to either 'mps' if you have M1/M2 or 'cpu'