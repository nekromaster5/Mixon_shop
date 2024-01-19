const gulp = require('gulp');
const rigger = require('gulp-rigger');

// Задача для обработки каталога
gulp.task('catalog', function() {
  return gulp.src('partsix/catalog.html') // Путь к вашему каталогу
    .pipe(rigger({
      includePaths: ['partsix'] // Папка, где находятся header.html и другие файлы
    }))
    .pipe(gulp.dest('dist')); // Путь к выходной папке, куда сохранится обработанный файл
});

// Задача по умолчанию, которая будет выполняться при запуске команды 'gulp'
gulp.task('default', gulp.series('catalog'));
