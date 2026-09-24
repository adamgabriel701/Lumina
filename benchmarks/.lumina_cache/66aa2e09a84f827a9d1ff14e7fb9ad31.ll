; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
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
define i64 @"main"()
{
main_entry:
  call void @"GC_init"()
  br label %"main_body"
main_body:
  %"n" = alloca i64
  store i64 200, i64* %"n"
  %"n_load" = load i64, i64* %"n"
  %"n_load.1" = load i64, i64* %"n"
  %"mul" = mul i64 %"n_load", %"n_load.1"
  %"size" = alloca i64
  store i64 %"mul", i64* %"size"
  %"size_load" = load i64, i64* %"size"
  %"alloc_size" = mul i64 %"size_load", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"a" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"a"
  %"size_load.1" = load i64, i64* %"size"
  %"alloc_size.1" = mul i64 %"size_load.1", 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"b" = alloca i64*
  %"alloc_bitcast.1" = bitcast i8* %"alloc_call.1" to i64*
  store i64* %"alloc_bitcast.1", i64** %"b"
  %"size_load.2" = load i64, i64* %"size"
  %"alloc_size.2" = mul i64 %"size_load.2", 8
  %"alloc_call.2" = call i8* @"GC_malloc"(i64 %"alloc_size.2")
  %"c" = alloca i64*
  %"alloc_bitcast.2" = bitcast i8* %"alloc_call.2" to i64*
  store i64* %"alloc_bitcast.2", i64** %"c"
  %"size_load.3" = load i64, i64* %"size"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", %"size_load.3"
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"i_load" = load i64, i64* %"i"
  %"mod" = srem i64 %"i_load", 10
  %"a_load" = load i64*, i64** %"a"
  %"i_load.1" = load i64, i64* %"i"
  %".11" = getelementptr i64, i64* %"a_load", i64 %"i_load.1"
  store i64 %"mod", i64* %".11"
  %"i_load.2" = load i64, i64* %"i"
  %"mul.1" = mul i64 %"i_load.2", 2
  %"mod.1" = srem i64 %"mul.1", 10
  %"b_load" = load i64*, i64** %"b"
  %"i_load.3" = load i64, i64* %"i"
  %".13" = getelementptr i64, i64* %"b_load", i64 %"i_load.3"
  store i64 %"mod.1", i64* %".13"
  %"c_load" = load i64*, i64** %"c"
  %"i_load.4" = load i64, i64* %"i"
  %".15" = getelementptr i64, i64* %"c_load", i64 %"i_load.4"
  store i64 0, i64* %".15"
  br label %"for_inc"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %"n_load.2" = load i64, i64* %"n"
  %"i.1" = alloca i64
  store i64 0, i64* %"i.1"
  br label %"for_cond.2"
for_cond.2:
  %"for_curr.1" = load i64, i64* %"i.1"
  %"for_cond.3" = icmp slt i64 %"for_curr.1", %"n_load.2"
  br i1 %"for_cond.3", label %"for_body.1", label %"for_end.1"
for_body.1:
  %"n_load.3" = load i64, i64* %"n"
  %"j" = alloca i64
  store i64 0, i64* %"j"
  br label %"for_cond.4"
for_inc.1:
  %"for_curr_inc.3" = load i64, i64* %"i.1"
  %"for_next.3" = add i64 %"for_curr_inc.3", 1
  store i64 %"for_next.3", i64* %"i.1"
  br label %"for_cond.2"
for_end.1:
  %".44" = bitcast [16 x i8]* @"str_0" to i8*
  %".45" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".45", i8* %".44")
  %"c_load.2" = load i64*, i64** %"c"
  %".46" = getelementptr i64, i64* %"c_load.2", i64 0
  %"ptr_idx_load.2" = load i64, i64* %".46"
  %".47" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".47")
  %".48" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".48", i64 %"ptr_idx_load.2")
  %".49" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".49")
  %".50" = bitcast [20 x i8]* @"str_5" to i8*
  %".51" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".51", i8* %".50")
  %"c_load.3" = load i64*, i64** %"c"
  %"n_load.8" = load i64, i64* %"n"
  %"mul.6" = mul i64 199, %"n_load.8"
  %"add.4" = add i64 %"mul.6", 199
  %".52" = getelementptr i64, i64* %"c_load.3", i64 %"add.4"
  %"ptr_idx_load.3" = load i64, i64* %".52"
  %".53" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".53")
  %".54" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".54", i64 %"ptr_idx_load.3")
  %".55" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".55")
  ret i64 0
for_cond.4:
  %"for_curr.2" = load i64, i64* %"j"
  %"for_cond.5" = icmp slt i64 %"for_curr.2", %"n_load.3"
  br i1 %"for_cond.5", label %"for_body.2", label %"for_end.2"
for_body.2:
  %"sum" = alloca i64
  store i64 0, i64* %"sum"
  %"n_load.4" = load i64, i64* %"n"
  %"k" = alloca i64
  store i64 0, i64* %"k"
  br label %"for_cond.6"
for_inc.2:
  %"for_curr_inc.2" = load i64, i64* %"j"
  %"for_next.2" = add i64 %"for_curr_inc.2", 1
  store i64 %"for_next.2", i64* %"j"
  br label %"for_cond.4"
for_end.2:
  br label %"for_inc.1"
for_cond.6:
  %"for_curr.3" = load i64, i64* %"k"
  %"for_cond.7" = icmp slt i64 %"for_curr.3", %"n_load.4"
  br i1 %"for_cond.7", label %"for_body.3", label %"for_end.3"
for_body.3:
  %"sum_load" = load i64, i64* %"sum"
  %"a_load.1" = load i64*, i64** %"a"
  %"i_load.5" = load i64, i64* %"i.1"
  %"n_load.5" = load i64, i64* %"n"
  %"mul.2" = mul i64 %"i_load.5", %"n_load.5"
  %"k_load" = load i64, i64* %"k"
  %"add" = add i64 %"mul.2", %"k_load"
  %".30" = getelementptr i64, i64* %"a_load.1", i64 %"add"
  %"ptr_idx_load" = load i64, i64* %".30"
  %"b_load.1" = load i64*, i64** %"b"
  %"k_load.1" = load i64, i64* %"k"
  %"n_load.6" = load i64, i64* %"n"
  %"mul.3" = mul i64 %"k_load.1", %"n_load.6"
  %"j_load" = load i64, i64* %"j"
  %"add.1" = add i64 %"mul.3", %"j_load"
  %".31" = getelementptr i64, i64* %"b_load.1", i64 %"add.1"
  %"ptr_idx_load.1" = load i64, i64* %".31"
  %"mul.4" = mul i64 %"ptr_idx_load", %"ptr_idx_load.1"
  %"add.2" = add i64 %"sum_load", %"mul.4"
  store i64 %"add.2", i64* %"sum"
  br label %"for_inc.3"
for_inc.3:
  %"for_curr_inc.1" = load i64, i64* %"k"
  %"for_next.1" = add i64 %"for_curr_inc.1", 1
  store i64 %"for_next.1", i64* %"k"
  br label %"for_cond.6"
for_end.3:
  %"sum_load.1" = load i64, i64* %"sum"
  %"c_load.1" = load i64*, i64** %"c"
  %"i_load.6" = load i64, i64* %"i.1"
  %"n_load.7" = load i64, i64* %"n"
  %"mul.5" = mul i64 %"i_load.6", %"n_load.7"
  %"j_load.1" = load i64, i64* %"j"
  %"add.3" = add i64 %"mul.5", %"j_load.1"
  %".36" = getelementptr i64, i64* %"c_load.1", i64 %"add.3"
  store i64 %"sum_load.1", i64* %".36"
  br label %"for_inc.2"
}

@"str_0" = constant [16 x i8] c"Matriz C[0][0]:\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [20 x i8] c"Matriz C[199][199]:\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"