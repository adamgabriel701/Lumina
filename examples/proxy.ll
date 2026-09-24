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
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"porta_proxy" = alloca i64
  store i64 8080, i64* %"porta_proxy"
  %"porta_backend" = alloca i64
  store i64 3000, i64* %"porta_backend"
  %"porta_proxy_load" = load i64, i64* %"porta_proxy"
  %"iniciar_call" = call i64 @"iniciar"(i64 %"porta_proxy_load")
  %"server_fd" = alloca i64
  store i64 %"iniciar_call", i64* %"server_fd"
  %"server_fd_load" = load i64, i64* %"server_fd"
  %"icmp" = icmp slt i64 %"server_fd_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %".11" = bitcast [32 x i8]* @"str_0" to i8*
  %"porta_proxy_load.1" = load i64, i64* %"porta_proxy"
  %".12" = bitcast [4 x i8]* @"str_1" to i8*
  %"num_to_str" = alloca [64 x i8]
  %"num_to_str_ptr" = bitcast [64 x i8]* %"num_to_str" to i8*
  %"num_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr", i64 64, i8* %".12", i64 %"porta_proxy_load.1")
  %"sconcat_len1" = call i64 @"strlen"(i8* %".11")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"num_to_str_ptr")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".11")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"num_to_str_ptr")
  %".13" = bitcast [3 x i8]* @"str_2" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %"sconcat_buf")
  %".14" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %"ret_trunc" = trunc i64 1 to i32
  ret i32 %"ret_trunc"
if_else:
  br label %"if_end"
if_end:
  %".17" = bitcast [37 x i8]* @"str_4" to i8*
  %"porta_proxy_load.2" = load i64, i64* %"porta_proxy"
  %".18" = bitcast [4 x i8]* @"str_5" to i8*
  %"num_to_str.1" = alloca [64 x i8]
  %"num_to_str_ptr.1" = bitcast [64 x i8]* %"num_to_str.1" to i8*
  %"num_to_str_call.1" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr.1", i64 64, i8* %".18", i64 %"porta_proxy_load.2")
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %".17")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %"num_to_str_ptr.1")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %".17")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %"num_to_str_ptr.1")
  %".19" = bitcast [16 x i8]* @"str_6" to i8*
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"sconcat_buf.1")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %".19")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"sconcat_buf.1")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %".19")
  %"porta_backend_load" = load i64, i64* %"porta_backend"
  %".20" = bitcast [4 x i8]* @"str_7" to i8*
  %"num_to_str.2" = alloca [64 x i8]
  %"num_to_str_ptr.2" = bitcast [64 x i8]* %"num_to_str.2" to i8*
  %"num_to_str_call.2" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr.2", i64 64, i8* %".20", i64 %"porta_backend_load")
  %"sconcat_len1.3" = call i64 @"strlen"(i8* %"sconcat_buf.2")
  %"sconcat_len2.3" = call i64 @"strlen"(i8* %"num_to_str_ptr.2")
  %"sconcat_sum.3" = add i64 %"sconcat_len1.3", %"sconcat_len2.3"
  %"sconcat_total.3" = add i64 %"sconcat_sum.3", 1
  %"sconcat_buf.3" = call i8* @"GC_malloc"(i64 %"sconcat_total.3")
  %"sconcat_cpy.3" = call i8* @"strcpy"(i8* %"sconcat_buf.3", i8* %"sconcat_buf.2")
  %"sconcat_cat.3" = call i8* @"strcat"(i8* %"sconcat_buf.3", i8* %"num_to_str_ptr.2")
  %".21" = bitcast [3 x i8]* @"str_8" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %"sconcat_buf.3")
  %".22" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %"client_addr_stack" = alloca [16 x i8]
  %"client_addr_first" = getelementptr [16 x i8], [16 x i8]* %"client_addr_stack", i32 0, i32 0
  %"client_addr" = alloca i8*
  store i8* %"client_addr_first", i8** %"client_addr"
  %"client_len_ptr_stack" = alloca [4 x i8]
  %"client_len_ptr_first" = getelementptr [4 x i8], [4 x i8]* %"client_len_ptr_stack", i32 0, i32 0
  %"client_len_ptr" = alloca i8*
  store i8* %"client_len_ptr_first", i8** %"client_len_ptr"
  %"client_len_ptr_load" = load i8*, i8** %"client_len_ptr"
  %"idx_ptr" = getelementptr i8, i8* %"client_len_ptr_load", i64 0
  %"elem_trunc" = trunc i64 16 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"request_buffer_stack" = alloca [4096 x i8]
  %"request_buffer_first" = getelementptr [4096 x i8], [4096 x i8]* %"request_buffer_stack", i32 0, i32 0
  %"request_buffer" = alloca i8*
  store i8* %"request_buffer_first", i8** %"request_buffer"
  %"response_buffer_stack" = alloca [4096 x i8]
  %"response_buffer_first" = getelementptr [4096 x i8], [4096 x i8]* %"response_buffer_stack", i32 0, i32 0
  %"response_buffer" = alloca i8*
  store i8* %"response_buffer_first", i8** %"response_buffer"
  %".28" = bitcast [73 x i8]* @"str_10" to i8*
  %"bad_gateway" = alloca i8*
  store i8* %".28", i8** %"bad_gateway"
  %"bad_gateway_load" = load i8*, i8** %"bad_gateway"
  %"len_str" = call i64 @"strlen"(i8* %"bad_gateway_load")
  %"bad_gateway_len" = alloca i64
  store i64 %"len_str", i64* %"bad_gateway_len"
  br label %"while_cond"
while_cond:
  br i1 1, label %"while_body", label %"while_end"
while_body:
  %"server_fd_load.1" = load i64, i64* %"server_fd"
  %"client_addr_load" = load i8*, i8** %"client_addr"
  %"client_len_ptr_load.1" = load i8*, i8** %"client_len_ptr"
  %"accept_call" = call i64 @"accept"(i64 %"server_fd_load.1", i8* %"client_addr_load", i8* %"client_len_ptr_load.1")
  %"client_fd" = alloca i64
  store i64 %"accept_call", i64* %"client_fd"
  %"client_fd_load" = load i64, i64* %"client_fd"
  %"icmp.1" = icmp slt i64 %"client_fd_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
while_end:
  %"ret_trunc.1" = trunc i64 0 to i32
  ret i32 %"ret_trunc.1"
if_then.1:
  br label %"while_cond"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"client_fd_load.1" = load i64, i64* %"client_fd"
  %"request_buffer_load" = load i8*, i8** %"request_buffer"
  %"recv_call" = call i64 @"recv"(i64 %"client_fd_load.1", i8* %"request_buffer_load", i64 4096, i64 0)
  %"bytes_lidos" = alloca i64
  store i64 %"recv_call", i64* %"bytes_lidos"
  %"bytes_lidos_load" = load i64, i64* %"bytes_lidos"
  %"icmp.2" = icmp sle i64 %"bytes_lidos_load", 0
  br i1 %"icmp.2", label %"if_then.2", label %"if_else.2"
if_then.2:
  %"client_fd_load.2" = load i64, i64* %"client_fd"
  %"close_call" = call i64 @"close"(i64 %"client_fd_load.2")
  br label %"while_cond"
if_else.2:
  br label %"if_end.2"
if_end.2:
  %"porta_backend_load.1" = load i64, i64* %"porta_backend"
  %"conectar_backend_call" = call i64 @"conectar_backend"(i64 %"porta_backend_load.1")
  %"backend_fd" = alloca i64
  store i64 %"conectar_backend_call", i64* %"backend_fd"
  %"backend_fd_load" = load i64, i64* %"backend_fd"
  %"icmp.3" = icmp slt i64 %"backend_fd_load", 0
  br i1 %"icmp.3", label %"if_then.3", label %"if_else.3"
if_then.3:
  %"client_fd_load.3" = load i64, i64* %"client_fd"
  %"bad_gateway_load.1" = load i8*, i8** %"bad_gateway"
  %"bad_gateway_len_load" = load i64, i64* %"bad_gateway_len"
  %"send_call" = call i64 @"send"(i64 %"client_fd_load.3", i8* %"bad_gateway_load.1", i64 %"bad_gateway_len_load", i64 0)
  %"client_fd_load.4" = load i64, i64* %"client_fd"
  %"close_call.1" = call i64 @"close"(i64 %"client_fd_load.4")
  br label %"while_cond"
if_else.3:
  br label %"if_end.3"
if_end.3:
  %"backend_fd_load.1" = load i64, i64* %"backend_fd"
  %"request_buffer_load.1" = load i8*, i8** %"request_buffer"
  %"bytes_lidos_load.1" = load i64, i64* %"bytes_lidos"
  %"send_call.1" = call i64 @"send"(i64 %"backend_fd_load.1", i8* %"request_buffer_load.1", i64 %"bytes_lidos_load.1", i64 0)
  %"backend_fd_load.2" = load i64, i64* %"backend_fd"
  %"response_buffer_load" = load i8*, i8** %"response_buffer"
  %"recv_call.1" = call i64 @"recv"(i64 %"backend_fd_load.2", i8* %"response_buffer_load", i64 4096, i64 0)
  %"bytes_resp" = alloca i64
  store i64 %"recv_call.1", i64* %"bytes_resp"
  %"bytes_resp_load" = load i64, i64* %"bytes_resp"
  %"icmp.4" = icmp sgt i64 %"bytes_resp_load", 0
  br i1 %"icmp.4", label %"if_then.4", label %"if_else.4"
if_then.4:
  %"client_fd_load.5" = load i64, i64* %"client_fd"
  %"response_buffer_load.1" = load i8*, i8** %"response_buffer"
  %"bytes_resp_load.1" = load i64, i64* %"bytes_resp"
  %"send_call.2" = call i64 @"send"(i64 %"client_fd_load.5", i8* %"response_buffer_load.1", i64 %"bytes_resp_load.1", i64 0)
  br label %"if_end.4"
if_else.4:
  br label %"if_end.4"
if_end.4:
  %"backend_fd_load.3" = load i64, i64* %"backend_fd"
  %"close_call.2" = call i64 @"close"(i64 %"backend_fd_load.3")
  %"client_fd_load.6" = load i64, i64* %"client_fd"
  %"close_call.3" = call i64 @"close"(i64 %"client_fd_load.6")
  br label %"while_cond"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
declare i64 @"socket"(i64 %".1", i64 %".2", i64 %".3")

declare i64 @"setsockopt"(i64 %".1", i64 %".2", i64 %".3", i8* %".4", i64 %".5")

declare i64 @"bind"(i64 %".1", i8* %".2", i64 %".3")

declare i64 @"listen"(i64 %".1", i64 %".2")

declare i64 @"accept"(i64 %".1", i8* %".2", i8* %".3")

declare i64 @"recv"(i64 %".1", i8* %".2", i64 %".3", i64 %".4")

declare i64 @"send"(i64 %".1", i8* %".2", i64 %".3", i64 %".4")

declare i64 @"close"(i64 %".1")

declare i64 @"connect"(i64 %".1", i8* %".2", i64 %".3")

define i64 @"iniciar"(i64 %".1")
{
iniciar_entry:
  %"porta" = alloca i64
  store i64 %".1", i64* %"porta"
  br label %"iniciar_body"
iniciar_body:
  %"socket_call" = call i64 @"socket"(i64 2, i64 1, i64 0)
  %"server_fd" = alloca i64
  store i64 %"socket_call", i64* %"server_fd"
  %"server_fd_load" = load i64, i64* %"server_fd"
  %"icmp" = icmp slt i64 %"server_fd_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"neg" = sub i64 0, 1
  ret i64 %"neg"
if_else:
  br label %"if_end"
if_end:
  %"reuse_stack" = alloca [4 x i8]
  %"reuse_first" = getelementptr [4 x i8], [4 x i8]* %"reuse_stack", i32 0, i32 0
  %"reuse" = alloca i8*
  store i8* %"reuse_first", i8** %"reuse"
  %"reuse_load" = load i8*, i8** %"reuse"
  %"idx_ptr" = getelementptr i8, i8* %"reuse_load", i64 0
  %"elem_trunc" = trunc i64 1 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"server_fd_load.1" = load i64, i64* %"server_fd"
  %"reuse_load.1" = load i8*, i8** %"reuse"
  %"setsockopt_call" = call i64 @"setsockopt"(i64 %"server_fd_load.1", i64 1, i64 2, i8* %"reuse_load.1", i64 4)
  %"addr_stack" = alloca [16 x i8]
  %"addr_first" = getelementptr [16 x i8], [16 x i8]* %"addr_stack", i32 0, i32 0
  %"addr" = alloca i8*
  store i8* %"addr_first", i8** %"addr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", 16
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"addr_load" = load i8*, i8** %"addr"
  %"i_load" = load i64, i64* %"i"
  %"idx_ptr.1" = getelementptr i8, i8* %"addr_load", i64 %"i_load"
  %"elem_trunc.1" = trunc i64 0 to i8
  store i8 %"elem_trunc.1", i8* %"idx_ptr.1"
  br label %"for_inc"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %"addr_load.1" = load i8*, i8** %"addr"
  %"idx_ptr.2" = getelementptr i8, i8* %"addr_load.1", i64 0
  %"elem_trunc.2" = trunc i64 2 to i8
  store i8 %"elem_trunc.2", i8* %"idx_ptr.2"
  %"porta_load" = load i64, i64* %"porta"
  %"div" = sdiv i64 %"porta_load", 256
  %"addr_load.2" = load i8*, i8** %"addr"
  %"idx_ptr.3" = getelementptr i8, i8* %"addr_load.2", i64 2
  %"elem_trunc.3" = trunc i64 %"div" to i8
  store i8 %"elem_trunc.3", i8* %"idx_ptr.3"
  %"porta_load.1" = load i64, i64* %"porta"
  %"mod" = srem i64 %"porta_load.1", 256
  %"addr_load.3" = load i8*, i8** %"addr"
  %"idx_ptr.4" = getelementptr i8, i8* %"addr_load.3", i64 3
  %"elem_trunc.4" = trunc i64 %"mod" to i8
  store i8 %"elem_trunc.4", i8* %"idx_ptr.4"
  %"server_fd_load.2" = load i64, i64* %"server_fd"
  %"addr_load.4" = load i8*, i8** %"addr"
  %"bind_call" = call i64 @"bind"(i64 %"server_fd_load.2", i8* %"addr_load.4", i64 16)
  %"bind_res" = alloca i64
  store i64 %"bind_call", i64* %"bind_res"
  %"bind_res_load" = load i64, i64* %"bind_res"
  %"icmp.1" = icmp slt i64 %"bind_res_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"server_fd_load.3" = load i64, i64* %"server_fd"
  %"close_call" = call i64 @"close"(i64 %"server_fd_load.3")
  %"neg.1" = sub i64 0, 1
  ret i64 %"neg.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"server_fd_load.4" = load i64, i64* %"server_fd"
  %"listen_call" = call i64 @"listen"(i64 %"server_fd_load.4", i64 10)
  %"server_fd_load.5" = load i64, i64* %"server_fd"
  ret i64 %"server_fd_load.5"
}

define i64 @"conectar_backend"(i64 %".1")
{
conectar_backend_entry:
  %"porta" = alloca i64
  store i64 %".1", i64* %"porta"
  br label %"conectar_backend_body"
conectar_backend_body:
  %"socket_call" = call i64 @"socket"(i64 2, i64 1, i64 0)
  %"fd" = alloca i64
  store i64 %"socket_call", i64* %"fd"
  %"fd_load" = load i64, i64* %"fd"
  %"icmp" = icmp slt i64 %"fd_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"neg" = sub i64 0, 1
  ret i64 %"neg"
if_else:
  br label %"if_end"
if_end:
  %"addr_stack" = alloca [16 x i8]
  %"addr_first" = getelementptr [16 x i8], [16 x i8]* %"addr_stack", i32 0, i32 0
  %"addr" = alloca i8*
  store i8* %"addr_first", i8** %"addr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", 16
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"addr_load" = load i8*, i8** %"addr"
  %"i_load" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i8, i8* %"addr_load", i64 %"i_load"
  %"elem_trunc" = trunc i64 0 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  br label %"for_inc"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %"addr_load.1" = load i8*, i8** %"addr"
  %"idx_ptr.1" = getelementptr i8, i8* %"addr_load.1", i64 0
  %"elem_trunc.1" = trunc i64 2 to i8
  store i8 %"elem_trunc.1", i8* %"idx_ptr.1"
  %"porta_load" = load i64, i64* %"porta"
  %"div" = sdiv i64 %"porta_load", 256
  %"addr_load.2" = load i8*, i8** %"addr"
  %"idx_ptr.2" = getelementptr i8, i8* %"addr_load.2", i64 2
  %"elem_trunc.2" = trunc i64 %"div" to i8
  store i8 %"elem_trunc.2", i8* %"idx_ptr.2"
  %"porta_load.1" = load i64, i64* %"porta"
  %"mod" = srem i64 %"porta_load.1", 256
  %"addr_load.3" = load i8*, i8** %"addr"
  %"idx_ptr.3" = getelementptr i8, i8* %"addr_load.3", i64 3
  %"elem_trunc.3" = trunc i64 %"mod" to i8
  store i8 %"elem_trunc.3", i8* %"idx_ptr.3"
  %"addr_load.4" = load i8*, i8** %"addr"
  %"idx_ptr.4" = getelementptr i8, i8* %"addr_load.4", i64 4
  %"elem_trunc.4" = trunc i64 127 to i8
  store i8 %"elem_trunc.4", i8* %"idx_ptr.4"
  %"addr_load.5" = load i8*, i8** %"addr"
  %"idx_ptr.5" = getelementptr i8, i8* %"addr_load.5", i64 5
  %"elem_trunc.5" = trunc i64 0 to i8
  store i8 %"elem_trunc.5", i8* %"idx_ptr.5"
  %"addr_load.6" = load i8*, i8** %"addr"
  %"idx_ptr.6" = getelementptr i8, i8* %"addr_load.6", i64 6
  %"elem_trunc.6" = trunc i64 0 to i8
  store i8 %"elem_trunc.6", i8* %"idx_ptr.6"
  %"addr_load.7" = load i8*, i8** %"addr"
  %"idx_ptr.7" = getelementptr i8, i8* %"addr_load.7", i64 7
  %"elem_trunc.7" = trunc i64 1 to i8
  store i8 %"elem_trunc.7", i8* %"idx_ptr.7"
  %"fd_load.1" = load i64, i64* %"fd"
  %"addr_load.8" = load i8*, i8** %"addr"
  %"connect_call" = call i64 @"connect"(i64 %"fd_load.1", i8* %"addr_load.8", i64 16)
  %"res" = alloca i64
  store i64 %"connect_call", i64* %"res"
  %"res_load" = load i64, i64* %"res"
  %"icmp.1" = icmp slt i64 %"res_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"fd_load.2" = load i64, i64* %"fd"
  %"close_call" = call i64 @"close"(i64 %"fd_load.2")
  %"neg.1" = sub i64 0, 1
  ret i64 %"neg.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"fd_load.3" = load i64, i64* %"fd"
  ret i64 %"fd_load.3"
}

@"str_0" = constant [32 x i8] c"Erro ao iniciar proxy na porta \00"
@"str_1" = constant [4 x i8] c"%ld\00"
@"str_2" = constant [3 x i8] c"%s\00"
@"str_3" = constant [2 x i8] c"\0a\00"
@"str_4" = constant [37 x i8] c"\f0\9f\9a\80 Proxy Reverso rodando na porta \00"
@"str_5" = constant [4 x i8] c"%ld\00"
@"str_6" = constant [16 x i8] c" -> Backend na \00"
@"str_7" = constant [4 x i8] c"%ld\00"
@"str_8" = constant [3 x i8] c"%s\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [73 x i8] c"HTTP/1.1 502 Bad Gateway\0d\0aContent-Length: 24\0d\0a\0d\0a<h1>502 Bad Gateway</h1>\00"