# Dockerfile para PupiStock [Django + Tailwind]
FROM python:3.12-slim as base

# Etapa de build para Node/Tailwind
FROM node:20-slim as nodebuild
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY ./tailwind.config.js ./postcss.config.js ./ 
COPY ./pupistock/static_src ./static_src
RUN npx tailwindcss -c tailwind.config.js -i ./static_src/input.css -o ./static/css/tailwind.css --minify

# App Django
FROM base as final
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY --from=nodebuild /app/static/css/tailwind.css /app/static/css/tailwind.css
COPY . .
# Expone puerto por defecto
EXPOSE 8000
CMD ["gunicorn", "pupistock.wsgi:application", "--bind", "0.0.0.0:8000"]