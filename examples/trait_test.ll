; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Square" = type {i64}
declare i32 @"printf"(i8* %".1", ...)

declare i8* @"GC_malloc"(i64 %".1")

declare void @"GC_init"()

declare void @"GC_free"(i8* %".1")

declare i8* @"strcpy"(i8* %".1", i8* %".2")

declare i8* @"strcat"(i8* %".1", i8* %".2")

declare i64 @"strlen"(i8* %".1")

declare i32 @"snprintf"(i8* %".1", i64 %".2", i8* %".3", ...)

declare i8* @"strstr"(i8* %".1", i8* %".2")

declare i32 @"strncmp"(i8* %".1", i8* %".2", i64 %".3")

declare i64 @"atoi"(i8* %".1")

declare i32 @"strcmp"(i8* %".1", i8* %".2")

declare i8* @"strncpy"(i8* %".1", i8* %".2", i64 %".3")

@"stdin" = external global i8*
@"stdout" = external global i8*
@"stderr" = external global i8*
define void @"Square_draw"(%"Square"* %".1")
{
Square_draw_entry:
  %"self" = alloca %"Square"*
  store %"Square"* %".1", %"Square"** %"self"
  br label %"Square_draw_body"
Square_draw_body:
  %".5" = bitcast [21 x i8]* @"str_0" to i8*
  %".6" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".6", i8* %".5")
  %".7" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".7")
  ret void
}

define i64 @"Square_get_area"(%"Square"* %".1")
{
Square_get_area_entry:
  %"self" = alloca %"Square"*
  store %"Square"* %".1", %"Square"** %"self"
  br label %"Square_get_area_body"
Square_get_area_body:
  %"mul" = mul i64 10, 10
  ret i64 %"mul"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [19 x i8]* @"str_3" to i8*
  %".8" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"sq" = alloca %"Square"*
  %"sq_storage_raw" = call i8* @"GC_malloc"(i64 8)
  %"sq_storage" = bitcast i8* %"sq_storage_raw" to %"Square"*
  store %"Square" {i64 0}, %"Square"* %"sq_storage"
  store %"Square"* %"sq_storage", %"Square"** %"sq"
  %"sq_load" = load %"Square"*, %"Square"** %"sq"
  %"size_ptr" = getelementptr %"Square", %"Square"* %"sq_load", i32 0, i32 0
  store i64 10, i64* %"size_ptr"
  %"sq_load.1" = load %"Square"*, %"Square"** %"sq"
  call void @"Square_draw"(%"Square"* %"sq_load.1")
  %"sq_load.2" = load %"Square"*, %"Square"** %"sq"
  %"Square_get_area_call" = call i64 @"Square_get_area"(%"Square"* %"sq_load.2")
  %"area" = alloca i64
  store i64 %"Square_get_area_call", i64* %"area"
  %".14" = bitcast [7 x i8]* @"str_6" to i8*
  %".15" = bitcast [3 x i8]* @"str_7" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".15", i8* %".14")
  %"area_load" = load i64, i64* %"area"
  %".16" = bitcast [2 x i8]* @"str_8" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [4 x i8]* @"str_9" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".17", i64 %"area_load")
  %".18" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [21 x i8] c"Desenhando Square...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [19 x i8] c"Testando Traits...\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c"\0a\00"
@"str_6" = constant [7 x i8] c"\c3\81rea:\00"
@"str_7" = constant [3 x i8] c"%s\00"
@"str_8" = constant [2 x i8] c" \00"
@"str_9" = constant [4 x i8] c"%ld\00"
@"str_10" = constant [2 x i8] c"\0a\00"